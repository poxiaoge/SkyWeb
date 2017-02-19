from flask import Blueprint

main = Blueprint('main',__name__,static_folder='static',template_folder='templates')

from . import views
from ..models import    Permission

@main.app_context_processor
def inject_permissions():
    return dict(Permission = Permission)