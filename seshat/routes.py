from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, current_user, login_required
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
            query_results.owners.append(current_user)
            flash(str(add_book_form.title.data) + ' added to your account!', 'success')
        else:
            book = Book(title=add_book_form.title.data, author=add_book_form.author.data)
            book.owners.append(current_user)
            db.session.add(book)
            flash(str(add_book_form.title.data) + ' successfully added to DB!', 'success')
        db.session.commit()
        return redirect(url_for('home'))
    # else:
    #     flash('An unknown error occurred. Please try again later.', 'danger')
    return render_template('add_book.html', title='Add A Book', form=add_book_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    user_books = Book.query.join(User.books).filter(User.id == current_user.id).all()
    update_account_form = UpdateAccountForm()
    if update_account_form.validate_on_submit():
        current_user.username = update_account_form.username.data
        current_user.email = update_account_form.email.data
        db.session.commit()
        flash('Account information has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        update_account_form.username.data = current_user.username
        update_account_form.email.data = current_user.email
    return render_template('account.html', books=user_books, title='Account', profile_pic=profile_pic, form=update_account_form)


# TODO: If a user is logged in, then allow to add the book to the account.
@app.route('/search')
def search():
    return render_template('search.html', title='Search')


@app.route('/account_settings')
def account_settings():
    return render_template('account_settings.html')


@app.route('/additional_stats')
def additional_stats():
    return render_template('additional_stats.html')


@app.route('/my_books')
def my_books():
    return render_template('my_books.html')
