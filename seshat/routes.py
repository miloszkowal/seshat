from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_required
from seshat.forms import BookForm, RegistrationForm, LoginForm
from seshat.models import User, Book
from seshat import app

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


# TODO: Complete registration route. Not required for MVP
@app.route('/register')
def register():
    registration_form = RegistrationForm()
    # if registration_form.validate_on_submit():
    #     pass
    # else:
    #     flash('An unknown error occurred. Please try again later.', 'danger')
    return render_template('register.html', title='Register', form=registration_form)


@app.route('/login')
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        pass
    else:
        # flash('Invalid username or password.', 'danger')
        pass
    return render_template('login.html', title='Login', form=login_form)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    add_book_form = BookForm()
    # return render_template('add_book.html', title='Add A Book', form=add_book_form)
    if add_book_form.validate_on_submit():
        # book = Book(title=add_book_form.title.data, author=add_book_form.author.data)
        # db.session.add(book)
        # db.session.commit()
        flash(str(add_book_form.title.data) + ' successfully added to DB!', 'success')
        return redirect(url_for('home'))
    else:
        flash('An unknown error occurred. Please try again later.', 'danger')
        # return redirect(url_for('home'))
    return render_template('add_book.html', title='Add A Book', form=add_book_form)
