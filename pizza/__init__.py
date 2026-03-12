from flask import Blueprint

pizza = Blueprint(
    'pizza',
    __name__,
    template_folder='templates'
    )

from . import routes