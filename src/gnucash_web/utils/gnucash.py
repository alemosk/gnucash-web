"""GnuCash utility functions.

Mostly wrappers around piecash functions.
"""
import datetime
from contextlib import contextmanager
from decimal import Decimal

from werkzeug.exceptions import NotFound, Locked
from flask import request
import piecash
import sqlalchemy


class AccessDenied(Exception):
    """Database access was denied."""

    pass


class AccountNotFound(NotFound):
    """GnuCash Account was not found."""

    def __init__(self, fullname, *args, **kwargs):
        """Create error.

        :param fullname: Full name of the non-existent account
        :returns: New Exception

        """
        super().__init__(*args, **kwargs)
        self.account_name = fullname


class DatabaseLocked(Locked):
    """The Database is locked."""

    def __init__(self, *args, **kwargs):
        """Create error.

        :returns: New Exception

        """
        super().__init__(*args, **kwargs)


@contextmanager
def open_book(*args, **kwargs):
    """Open GnuCash book in the configured database.

    Should be used as context manager.

    Wraps around `piecash.open_book`. Parameters are passed to that function.

    :param open_if_lock: If not provided explicitly, this is read from `request.args`
    :returns: The book
    :raises DatabaseLocked: If the databased is being accessed by someone else and
      `open_if_lock` is not `True`
    :raises AccessDenied: If access to the database is denied by the SQL server.

    """
    try:
        if "open_if_lock" not in kwargs:
            kwargs["open_if_lock"] = request.args.get(
                "open_if_lock", default=False, type=bool
            )

        with piecash.open_book(*args, **kwargs) as book:
            yield book

    except piecash.GnucashException as e:
        if "Lock on the file" in str(e):
            raise DatabaseLocked()
        if "does not exist" in str(e):
            raise AccessDenied
        else:
            raise e

    except sqlalchemy.exc.OperationalError as e:
        if "Access denied" in str(e):
            raise AccessDenied from e
        else:
            raise e


def get_account(book, *args, **kwargs):
    """Get account in the book based on given filters.

    Wraps around `piecash.core.book.Book.accounts.all`. All parameters are passed to
    that function.

    :param book: The book containing the account.
    :returns:

    """
    try:
        return book.accounts.get(*args, **kwargs)
    except KeyError:
        raise AccountNotFound(*args, **kwargs)


def get_budget_amounts(book, account):
    amounts = book.session.query(piecash.BudgetAmount).filter(piecash.BudgetAmount.account == account)

    return amounts


def get_total_in_current_month(account):
    # draft
    balance_at_end_of_month = Decimal(str(account.get_balance(
        at_date=datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    )))

    return account.get_balance() - balance_at_end_of_month
