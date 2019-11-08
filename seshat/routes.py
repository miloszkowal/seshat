import os
import secrets
from datetime import datetime

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, g
from flask_login import login_user, logout_user, current_user, login_required

from sqlalchemy.exc import IntegrityError

from seshat.forms import (BookForm, RegistrationForm, LoginForm,
                          UpdateAccountForm, SearchForm, ResetPasswordRequestForm, ResetPasswordForm)
from seshat.models import User, Book
from seshat.email import send_password_reset_email
from seshat import app, db, bcrypt


@app.route('/')
@app.route('/home')
def home():
    books = Book.query.all()
    return render_template('home.html', books=books)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(registration_form.password.data).decode('utf-8')
        new_user = User(username=registration_form.username.data, email=registration_form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account for {registration_form.username.data} created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=registration_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            return redirect(url_for('account'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', title='Login', form=login_form)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    add_book_form = BookForm()
    if add_book_form.validate_on_submit():
        query_results = Book.query.filter_by(title=add_book_form.title.data).first()
        if query_results:
            try:
                query_results.owners.append(current_user)
                db.session.commit()
                flash(str(add_book_form.title.data) + ' added to your account!', 'success')
            except IntegrityError:
                flash('Book already in your account!', 'warning')
            except:  # TODO: Remove this later, as it is not PEP8 compliant.
                flash('An unknown error occurred. Please try again later.', 'danger')
        else:
            book = Book(title=add_book_form.title.data, author=add_book_form.author.data)
            book.owners.append(current_user)
            db.session.add(book)
            flash(str(add_book_form.title.data) + ' successfully added to DB!', 'success')
            db.session.commit()
        return redirect(url_for('my_books'))
    return render_template('add_book.html', title='Add A Book', form=add_book_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    count = Book.query.join(User.books).filter(User.id == current_user.id).count()
    pages = db.session.query(db.func.sum(Book.num_pages).label("Total_Pages")).join(User.books).filter(User.id == current_user.id).first()[0]
    profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    return render_template('account.html', title='Account', profile_pic=profile_pic, count=count, pages=pages)


# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.utcnow()
#         db.session.commit()
#         g.search_form = SearchForm()
#     # g.locale = str(get_locale())


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not g.search_form.validate():
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    posts, total = Book.search(g.search_form.q.data, page,
                               app.config['BOOKS_PER_PAGE'])
    next_url = url_for('search', q=g.search_form.q.data, page=page + 1) \
        if total > page * app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    update_account_form = UpdateAccountForm()
    if update_account_form.validate_on_submit():
        if update_account_form.picture.data:
            picture_file = save_picture(update_account_form.picture.data)
            current_user.profile_pic = picture_file
        current_user.username = update_account_form.username.data
        current_user.email = update_account_form.email.data
        db.session.commit()
        flash('Account information has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        update_account_form.username.data = current_user.username
        update_account_form.email.data = current_user.email
    return render_template('account_settings.html', title='Account Settings', form=update_account_form)


@app.route('/additional_stats')
@login_required
def additional_stats():
    title = 'Additional Stats'
    return render_template('additional_stats.html', title=title)


@app.route('/my_books')
@login_required
def my_books():
    title = 'My Books'
    user_books = current_user.books
    return render_template('my_books.html', title=title, books=user_books, count=len(user_books))


@app.route('/account/delete_account', methods=['POST'])
@login_required
def delete_account():
    User.query.filter(User.id == current_user.id).delete()
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def book(book_id):
    book = Book.query.get(book_id)
    owner_count = len(book.owners.all())
    return render_template('book.html', count=owner_count, title=book.title, book=book)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book_to_delete = Book.query.get_or_404(book_id)
    current_user.books.remove(book_to_delete)
    db.session.commit()
    return redirect(url_for('my_books'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    reset_password_request_form = ResetPasswordRequestForm()
    if reset_password_request_form.validate_on_submit():
        user = User.query.filter_by(email=reset_password_request_form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password', 'info')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=reset_password_request_form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('This token is invalid or expired.', 'danger')
        return redirect(url_for('home'))
    reset_password_form = ResetPasswordForm()
    if reset_password_form.validate_on_submit():
        user.set_password(reset_password_form.password.data)
        db.session.commit()
        flash('Your password has been reset!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=reset_password_form)
