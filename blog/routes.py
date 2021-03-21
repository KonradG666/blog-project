from flask import Flask, request, render_template, redirect, url_for, flash, session
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm, ContactForm
from blog.functools import login_required
import os

@app.route('/')
def index():
    all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
    return render_template("homepage.html", all_posts=all_posts)

def create_or_edit(form, entry_id=None):
    if form.validate_on_submit():
        if entry_id is None:
            entry = Entry(title=form.title.data, body=form.body.data, is_published=form.is_published.data)
            is_published = form.is_published.data
            if is_published == True:
                db.session.add(entry)
                flash('New post added')
            if is_published == False:
                db.session.add(entry)
                flash("Post created and saved in Drafts")
        else:
            entry = Entry.query.filter_by(id=entry_id).first_or_404()
            form.populate_obj(entry)
            flash('Post updated')
        db.session.commit()
        return None
    else:
        return redirect(url_for('index', errors=errors))

@app.route("/new-entry/", methods=["GET", "POST"])
@login_required
def create_entry():
   form = EntryForm()
   errors = None
   if request.method == 'POST':
       create_or_edit(form)
       return redirect(url_for('index', errors=errors))
   return render_template("entry_form.html", form=form, errors=errors)

@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
   entry = Entry.query.filter_by(id=entry_id).first_or_404()
   form = EntryForm(obj=entry)
   errors = None
   if request.method == 'POST':
      create_or_edit(form, entry_id=entry_id)
      return redirect(url_for('index', errors=errors))
   return render_template("edit_form.html", form=form, errors=errors)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = None
    next_url = request.args.get('next')
    if request.method == 'POST':
        if form.validate_on_submit():
            session['logged_in'] = True
            session.permanent = True
            flash("You are now logged in.", "OK")
            return redirect(next_url or url_for("login"))
        else:
            errors = form.errors
    return render_template("login_form.html", form=form, errors=errors)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        flash("You are now logged out.", "OK")
    return redirect(url_for('login'))

@app.route("/drafts/", methods=["GET", "POST"])
@login_required
def drafts():
    drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
    return render_template("drafts.html", drafts=drafts)

@app.route("/delete/<int:entry_id>")
@login_required
def delete_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Post deleted", "OK")
    return redirect(url_for('index'))

@app.route("/contact/", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            email = request.form["email"]
            title = request.form["title"]
            name = request.form["name"]
            content = request.form["email_content"]
            flash("Message Send.", "success")
    return render_template("/contact.html")
