import os
import secrets

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, g, current_app
from flask_login import current_user, login_required

from sqlalchemy.exc import IntegrityError

from seshat.main.forms import BookForm, UpdateAccountForm, SearchForm, TagForm

from seshat.models import User, Book, Author, Tagging
from seshat import db
from seshat.main import bp


@bp.route('/')
@bp.route('/home')
def home():
    return render_template('home.html', books=[])


@bp.route('/about')
def about():
    return render_template('about.html', title='About')


@bp.route('/add_book', methods=['GET', 'POST'])
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
            book = Book(title=add_book_form.title.data)
            split_name = add_book_form.author.data.split()
            author = Author(first_name=split_name[0], last_name=split_name[1])
            book.authors.append(author)
            book.owners.append(current_user)
            db.session.add(author)
            db.session.add(book)
            flash(str(add_book_form.title.data) + ' successfully added to DB!', 'success')
            db.session.commit()
        return redirect(url_for('main.my_books'))
    return render_template('add_book.html', title='Add A Book', form=add_book_form)


@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    count = Book.query.join(User.books).filter(User.id == current_user.id).count()
    pages = db.session.query(db.func.sum(Book.num_pages).label("Total_Pages")).join(User.books).filter(User.id == current_user.id).first()[0]
    profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    return render_template('account.html', title='Account', profile_pic=profile_pic, count=count, pages=pages)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        db.session.commit()
        g.search_form = SearchForm()
    # g.locale = str(get_locale())


@bp.route('/search', methods=['GET', 'POST'])
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.home'))
    page = request.args.get('page', 1, type=int)
    books, total = Book.search(g.search_form.q.data, page, 10)
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * 10 else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', books=books, next_url=next_url, prev_url=prev_url)


def save_picture(form_picture, _type):
    """
    Saves a picture to the file system
    """
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + ext
    if _type == 'account':
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
        output_size = (125, 125)
    elif _type == 'book':
        picture_path = os.path.join(current_app.root_path, 'static/book_covers', picture_fn)
        output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@bp.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    update_account_form = UpdateAccountForm()
    if update_account_form.validate_on_submit():
        if update_account_form.picture.data:
            picture_file = save_picture(update_account_form.picture.data, _type="account")
            current_user.profile_pic = picture_file
        current_user.username = update_account_form.username.data
        current_user.email = update_account_form.email.data
        db.session.commit()
        flash('Account information has been updated!', 'success')
        return redirect(url_for('main.account'))
    elif request.method == 'GET':
        update_account_form.username.data = current_user.username
        update_account_form.email.data = current_user.email
    return render_template('account_settings.html', title='Account Settings', form=update_account_form)


@bp.route('/additional_stats')
@login_required
def additional_stats():
    title = 'Additional Stats'
    return render_template('additional_stats.html', title=title)


@bp.route('/book/<int:book_id>/tags/', methods=['GET'])
@login_required
def get_tags(book_id):
    book = Book.query.get_or_404(book_id)
    tags = Tagging.query.filter_by(book_tags=book, user_tags=current_user)
    return tags.all()


@bp.route('/my_books', methods=['GET', 'POST'])
@login_required
def my_books():
    title = 'My Books'
    user_books = current_user.books
    test_tags = Tagging.query.filter_by(book=user_books[0], user=current_user).all()
    tag_form = TagForm()
    return render_template('my_books.html', title=title, books=user_books, count=len(user_books), tags=test_tags, form=tag_form)


@bp.route('/account/delete_account', methods=['POST'])
@login_required
def delete_account():
    User.query.filter(User.id == current_user.id).delete()
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('main.home'))


@bp.route('/book/<int:book_id>')
def book(book_id):
    book = Book.query.get(book_id)
    owner_count = len(book.owners.all())
    return render_template('book.html', count=owner_count, title=book.title, book=book)


@bp.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book_to_delete = Book.query.get_or_404(book_id)
    current_user.books.remove(book_to_delete)
    db.session.commit()
    return redirect(url_for('main.my_books'))


@bp.route('/author/<int:author_id>')
def author(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author.html', title=author.first_name, author=author)


@bp.route('/book/<int:book_id>/tags/', methods=['POST'])
@login_required
def update_tags(book_id):
    return redirect(url_for('main.my_books'))
