from functools import wraps
from flask_login import  current_user
from flask import abort
from models import Permission


def permission_required(permission):
    def decorator_func(f):
        @wraps(f)
        def wrap_funct(*args,**kwargs):
            if not current_user.have_permission(permission):
                return abort(403)
            return f(*args,**kwargs)
        return wrap_funct
    return decorator_func

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


