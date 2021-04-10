from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "helloworld!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_redirect():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def show_register_form():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        register_user = User.register(username,
                                      password,
                                      email,
                                      first_name,
                                      last_name)
        db.session.add(register_user)
        db.session.commit()
        session['user_id'] = register_user.username
        return redirect(f'/users/{register_user.username}')
    return render_template('register_form.j2', form=form)



@app.route('/login', methods=["GET", "POST"])
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('login_form.j2', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


@app.route('/users/<username>')
def show_user_page(username):
    if "user_id" not in session:
        flash("Sorry, Please Login First")
        return redirect('/')
    user = User.query.get_or_404(username)
    if user.username == session['user_id']:
        return render_template('user_page.j2', user=user)
    else:
        flash("Sorry, Please Register First")
        return redirect('/')


# Delete User
@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if "user_id" not in session:
        flash("Sorry, Please Login First")
        return redirect('/login')
    user = User.query.get_or_404(username)
    if user.username == session['user_id']:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id')
        return redirect('/')

    return redirect('/')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    if "user_id" not in session:
        flash("Sorry, Please Login First")
        return redirect('/login')
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    if user.username == session['user_id']:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title=title, content=content, user=user)
            db.session.add(new_feedback)
            db.session.commit()
            return redirect(f'/users/{user.username}')
        return render_template('feedback_form.j2', form=form, user=user)
    else:
        flash("You don't have access to that")
        return redirect('/')
        

@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    if "user_id" not in session:
        flash("Sorry, Please Login First")
        return redirect('/login')
    form = FeedbackForm()
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.user.username == session['user_id']:
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.add(feedback)
            db.session.commit()
            return redirect(f'/users/{feedback.user.username}')
        return render_template('edit_feedback.j2', form=form, feedback=feedback)
    else:
        flash("You don't have access to that")
        return redirect('/')
    

@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    if "user_id" not in session:
        flash("Sorry, Please Login First")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.user.username == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.user.username}')