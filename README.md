# Seshat: A Book Manager that Doesn't Suck

## Introduction

I got tired of goodreads and how a) poor their interface was, b) how every book was three stars because of the amount of people (and bots) on the platform, and c) how it was tied to Amazon, and thus probbaly harvesting a bunch of info on me for the purposes of selling me stuff.

So I designed to take matters into my own hands after other competitors proved lacking in functionality. So welcome to Seshat.

## What's in a Name?

Seshat is the Egyptian deity responsible for wisdom, knowledge, and writing. And since I like ancient Egypt and naming things after a deity is pretty cool, so Seshat was born. It doesn't roll quite off the tongue as some other term might, but oh well, it's meant to be an app for a single user anyway.

## Implementation

The backend is managed in Python (Flask), and connected to a SQLite DB on the user's local machine. See Installing the Alpha seciton for more. On the front end, this is written in Bootstrap, but there is some motivation to moving to React, Angular, or Vue.

## Installing the Alpha

1. Download or clone this repository
2. Open terminal, navigate to the location of this repository
3. Ensure you have a virtual environment running
4. Run `pip install -r requirements.txt`
5. Run the app by running `python main.py` This should run a flask server on localhost:5000
5. In your browser, go to localhost:5000. Congratulations! You're running the alpha

## Navigating the Alpha

Two users currently exist: `test_user@seshatapp.io` and `test_user2@seshatapp.io`. Both have passwords of `password`. Currently, there are three books in the database: all three of Edmund Morris' books on Theodore Roosevelt.
As it stands, you can do the following:

* Register as a new user
* Login in as an existing user (including any users you create)
* Add Books to the DB (and also to your account)
