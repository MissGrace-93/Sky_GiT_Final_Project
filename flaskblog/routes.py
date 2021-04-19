import flask_login
import sqlalchemy
from flask import render_template, flash, redirect, url_for, request, abort
from flaskext import mysql
from sqlalchemy import create_engine

from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, PostForm
from flaskblog.models import User, Post, Comments
from flask_login import login_user, current_user, logout_user, login_required
import datetime

engine = create_engine("mysql+mysqlconnector://admin3:@GitPa$$w0rd#@54.74.234.11/finalproject_group3")
Post.metadata.bind = engine

DBSession = sqlalchemy.orm.sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/home_page')
def home_page():
    return render_template('home_page.html')


@app.route('/blog_archive')
def blog_archive():
    q = request.args.get('q')

    if q:
        posts = session.query(Post).filter(Post.title.contains(q) |
                                           Post.content.contains(q))
    else:
        posts = session.query(Post).all()
    return render_template('blog_archive.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home_page'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comments.query.filter_by(post_id=post.id).all()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        comment = Comments(name=name, email=email, message=message, post_id=post.id)
        db.session.add(comment)
        post.comments += 1
        flash('Your comment has been submitted', 'success')
        db.session.commit()

        return redirect(request.url)
    return render_template('post.html', title=post.title, post=post, comments=comments)


# @app.route("/post/<int:post_id>", methods=['POST'])
# def post(post_id):
#     name = request.form.get('name')
#     email = request.form.get('email')
#     message = request.form.get('message')
#     comment = Comments(name=name, email=email, message=message, post_id=post.id)
#     db.session.add(comment)
#     post.comments += 1
#     flash('Your comment has been submitted', 'success')
#     db.session.commit()
#
#     return redirect(request.url)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=request.form['title'], content=request.form['content'], author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('blog_archive'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('blog_archive'))
