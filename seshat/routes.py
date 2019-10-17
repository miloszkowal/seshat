from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from seshat.forms import BookForm, RegistrationForm, LoginForm
from seshat.models import User, Book
from seshat import app, db, bcrypt

books = [
    {
        'title': 'The Rise of Theodore Roosevelt',
        'author': 'Edmund Morris',
        'date_posted': 'January 28, 2019',
        'content': 'Some Content'
    },
    {
        'title': 'Theodore Rex',
        'author': 'Edmund Morris',
        'date_posted': 'January 28, 2019',
        'content': 'Some Content'
    }
]


@app.route('/')
def home():
    return render_template('home.html', books=books)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated():
        return redirect(url_for('home'))
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(registration_form.password.data).decode('utf-8')
        new_user = User(username=registration_form.username.data, email=registration_form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account for {registration_form.username.data} created!', 'success')
        return redirect(url_for('login'))
    else:
        flash('An unknown error occurred. Please try again later.', 'danger')
    return render_template('register.html', title='Register', form=registration_form)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', title='Login', form=login_form)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    add_book_form = BookForm()
    # return render_template('add_book.html', title='Add A Book', form=add_book_form)
    if add_book_form.validate_on_submit():
        book = Book(title=add_book_form.title.data, author=add_book_form.author.data)
        db.session.add(book)
        db.session.commit()
        flash(str(add_book_form.title.data) + ' successfully added to DB!', 'success')
        return redirect(url_for('home'))
    else:
        flash('An unknown error occurred. Please try again later.', 'danger')
        # return redirect(url_for('home'))
    return render_template('add_book.html', title='Add A Book', form=add_book_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
def account():
    logout_user()
    return render_template('account.html', title='Account')
