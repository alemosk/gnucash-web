"""About page of GnuCash Web project"""

from flask import render_template, Blueprint

bp = Blueprint("about", __name__, url_prefix="/about")


@bp.route("/")
def about():
    return render_template("about.j2")
