from functools import wraps
from authentication import forbidden
from flask import g


def permission_required(permission):
    def decorators(f):
        @wraps(f)
        def wrap_func(*args,**kwargs):
            if not g.current_user.have_permission(permission):
                return forbidden('Insufficient permissions')
            return f(*args,**kwargs)
        return wrap_func
    return decorators