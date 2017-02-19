import os

from flask import render_template, redirect, request, flash, abort, make_response, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import main
from .forms import *
from .. import db
from ..decorators import permission_required, admin_required
from ..models import *


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(nickname=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=current_app.config.get('POST_PER_PAGE'),
                                                                     error_out=False)
    posts = pagination.items
    return render_template('user_msg.html', user=user, posts=posts, pagination=pagination)


@main.route('/user/<int:id>/get-icon')
def get_icon(id):
    pass


ALLOWED_EXTENTIONS = set(['png', 'gif', 'jpg', 'jpeg', 'ico'])


def allowed_check(filename):
    return "." in filename and filename.split(".")[-1] in ALLOWED_EXTENTIONS


@main.route('/user/<int:id>/set-icon', methods=['POST'])
@login_required
def set_icon(id):
    user = User.query.get_or_404(id)
    if current_user != user and not current_user.is_administer():
        abort(404)
    file_get = request.files.get('head-img')
    if not allowed_check(file_get.filename):
        flash('Invalid filename!')
        # return redirect(request.args.get('next') or url_for('main.edit_profile'))
        return redirect(url_for('main.edit_profile_admin', id=user.id) if current_user.is_administer() else url_for(
            'main.edit_profile'))
    filename = secure_filename(file_get.filename)
    new_filename = str(id) + "." + filename.split(".")[-1]
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'thumbnail', new_filename)
    file_get.save(file_path)
    # with open(file_path,'wb') as newfile:
    #     newfile.write(file_get.read())
    user.img_url_postfix = new_filename
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.user', username=user.nickname))


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated!')
        return redirect(url_for('main.user', username=current_user.nickname))
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', header='Edit Profile', form=form, user=current_user)


@admin_required
@login_required
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = AdminEditProfileForm(user=user)
    if form.validate_on_submit():
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        # db.session.commit()
        flash('Profile has been updated!')
        return redirect(url_for('main.user', username=user.nickname))
    print "test:%s" % user.nickname
    form.nickname.data = user.nickname
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', header='Admin Editor', form=form, user=user)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.have_permission(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, timestamp=datetime.utcnow(),
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config.get('POST_PER_PAGE'),
                                                                error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published!')
        return redirect(url_for('main.post', id=post.id, page=-1) + "#comments")
    page = request.args.get('page', 1, type=int)
    if (page == -1):
        page = (post.comments.count() - 1) / current_app.config.get('POST_PER_PAGE') + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config.get(
        'POST_PER_PAGE'), error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, pagination=pagination, form=form, comments=comments)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.is_administer():
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('This post has been modified!')
        return redirect(url_for('main.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form, id=id)


@main.route('/follow/<nickname>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user!')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You have already followed this user!')
        return redirect(url_for('main.index'))
    current_user.follow(user)
    flash('You have successfully followed this user!')
    return redirect(url_for('main.user', username=nickname))


@main.route('/unfollow/<nickname>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user!')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You have not followed this user!')
        return redirect(url_for('main.index'))
    current_user.unfollow(user)
    flash('You have unfollowed this user!')
    return redirect(url_for('main.user', username=nickname))


@main.route('/followers/<nickname>')
def followers(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config.get('POST_PER_PAGE'), error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of", endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followed-by/<nickname>')
def followed_by(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config.get('POST_PER_PAGE'), error_out=False)
    followed = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed", endpoint='.followed_by',
                           pagination=pagination, followed=followed)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=3600 * 24 * 30)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=3600 * 24 * 30)
    return resp


@main.route('/disable-comment/<int:id>')
@login_required
@permission_required(Permission.MANAGE_COMMENT)
def disable_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if not comment:
        flash('Invalid comment!')
        return redirect(request.args.get('next') or url_for('main.index'))
    if comment.disabled:
        flash('Invalid operation!')
        return redirect(request.args.get('next') or url_for('main.index'))
    comment.disabled = True
    db.session.add(comment)
    return redirect(request.args.get('next') or url_for('main.post', id=comment.post_id, page=1) + "#comments")


@main.route('/enable-comment/<int:id>')
@login_required
@permission_required(Permission.MANAGE_COMMENT)
def enable_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    if not comment:
        flash('Invalid comment!')
        return redirect(request.args.get('next') or url_for('main.index'))
    if not comment.disabled:
        flash('Invalid operation!')
        return redirect(request.args.get('next') or url_for('main.index'))
    comment.disabled = False
    db.session.add(comment)
    return redirect(request.args.get('next') or url_for('main.post', id=comment.post_id) + "#comments")


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404
