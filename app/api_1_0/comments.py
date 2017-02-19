from flask import jsonify, request, g, url_for,current_app

from app import db
from app.api_1_0.authentication import auth
from app.api_1_0.errors import forbidden
from app.models import User, Post,Comment
from . import api
from .decorators import permission_required
from ..models import Permission

@api.route('/comments/')
@auth.login_required
def get_comments():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.asc()).paginate(page,per_page=current_app.config.get('POST_PER_PAGE'),error_out=False)
    comments= pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments',page=page-1,_external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments',page=page+1,_external=True)
    return jsonify({
        'comments':[comment.to_json() for comment in comments],
        'prev':prev,
        'next':next,
        'count':pagination.total
    })




@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify({'comment':comment.to_json()})