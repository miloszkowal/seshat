# Seshat: A New Book Manager

## Introduction

Seshat was built from the ground up to be a response to the current book manager scene, which is dominated by Goodreads. It's designed with the user in mind, giving you full control over your books, collections, and friends (coming soon). It features a slick and adaptive user interface, a gorgeous way to interact with your books, and reading goals to keep you reading and growing your library. You have to see it to believe it.

## What's in a Name?

Seshat is the Egyptian deity responsible for wisdom, knowledge, and writing. And since I like ancient Egypt and naming things after a deity is pretty cool, so Seshat was born. It doesn't roll quite off the tongue as some other term might, but oh well, it's meant to be an app for a single user anyway.

## Implementation

The backend is managed in Python (Flask), and connected to a SQLite DB on the user's local machine. See Installing the Alpha section for more. On the front end, Seshat is written in Bootstrap, but there is some motivation to move to React, Angular, or Vue.

## Installing the Alpha

1. Download or clone this repository
2. Open terminal, navigate to the location of this repository
3. Ensure you have a virtual environment running
4. Run `pip install -r requirements.txt`
5. Run the app by running `python main.py` This should run a flask server on localhost:5000
5. Congratulations! You're running the alpha

## Navigating the Alpha

Two users currently exist: `test_user@seshatapp.io` and `test_user2@seshatapp.io`. Both have passwords of `password`. Currently, there are three books in the database: all three of Edmund Morris' books on Theodore Roosevelt.
As it stands, you can do the following:

* Register as a new user
* Login in as an existing user (including any users you create)
* Add Books to the DB (and also to your account) and remove books from your account
* Make changes to your account (including changing your profile picture and deleting the account)

## Adding Issues

If you notice a bug or would like to suggest an additional feature, please open an issue on GitHub.
