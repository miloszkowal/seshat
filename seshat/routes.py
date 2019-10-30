import os
import secrets

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, current_user, login_required

from sqlalchemy.exc import IntegrityError

from seshat.forms import BookForm, RegistrationForm, LoginForm, UpdateAccountForm
from seshat.models import User, Book
from seshat import app, db, bcrypt


@app.route('/')
@app.route('/home')
def home():
    books = Book.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    else:
        return render_template('home.html', books=books)


@app.route('/about')
def about():
    return render_template('about.html', title='About')

# TODO: add salting


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
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            return redirect(url_for('home'))
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
            except:
                flash('An unknown error occurred. Please try again later.', 'danger')
        else:
            book = Book(title=add_book_form.title.data, author=add_book_form.author.data)
            book.owners.append(current_user)
            db.session.add(book)
            flash(str(add_book_form.title.data) + ' successfully added to DB!', 'success')
        return redirect(url_for('home'))
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


@app.route('/search')
def search():
    return render_template('search.html', title='Search')


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


@app.route('/account_settings')
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
    return render_template('additional_stats.html')


@app.route('/my_books')
@login_required
def my_books():
    title = 'My Books'
    count = Book.query.join(User.books).filter(User.id == current_user.id).count()
    user_books = Book.query.join(User.books).filter(User.id == current_user.id).all()
    return render_template('my_books.html', title=title, books=user_books, count=count)


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
    return render_template('book.html', title=book.title, book=book)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book_to_delete = Book.query.get_or_404(book_id)
    current_user.books.remove(book_to_delete)
    db.session.commit()
    return redirect(url_for('my_books'))
