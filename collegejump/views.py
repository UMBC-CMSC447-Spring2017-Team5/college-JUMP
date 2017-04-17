import datetime
import flask
from flask_login import login_user, logout_user, login_required
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from collegejump import app
from collegejump import forms, models, database

@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)


@app.route('/')
#@app.route('/index.html')
def front_page():
    return flask.render_template('index.html',
                                 __version__=app.config["VERSION"])


@app.route('/calendar.html')
def calendar_page():
    return flask.render_template('calendar.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # If the login form is successfully POSTed to us here, try to log the user
    # in. Otherwise, render the page as normal.
    form = forms.LoginForm()
    if form.validate_on_submit():
        app.logger.info("Attempting to log in {}... ".format(form.email.data), end="")
        email = form.email.data
        password = form.password.data

        try:
            user = models.User.query.filter_by(email=email).one()
            if user.check_password(password):
                # Modify the session so that the user is logged in.
                success = login_user(user)
                if success:
                    app.logger.info("success.")
                    return form.redirect()
                else:
                    # If the login failed, here, it's not because of the
                    # password. Maybe the user is inactive?
                    app.logger.info("login failed unexpectedly")

                    # Fall through to the failure handler.

        except MultipleResultsFound:
            # This is actually really bad, and means the database is very broken.
            raise

        except NoResultFound as e:
            print("no users with email '{}' found: {}".format(email, e))
            # Fall through to the failure handler.

        # If we reach here, the login has failed.
        app.logger.info("failure.")

    return flask.render_template('login.html', form=form,
                                 __version__=app.config["VERSION"])

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return flask.redirect(flask.url_for('front_page'))

@app.route('/account.html')
def acct_page():
    return flask.render_template('account.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")


@app.route('/announcements.html')
def announ_page():
    return flask.render_template('announcements.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")


@app.route('/edit_accounts', methods=['GET', 'POST'])
def edit_acct_page():
    # If the Create Acct form is successfully POSTed to us here, try to log the user
    # in. Otherwise, render the page as normal.
    form = forms.UserInfoForm()
    if form.validate_on_submit():
        app.logger.info("Attempting to create user... ", end="")
        user = models.User(form.email.data, form.password.data)
        user.name = form.name.data
        user.admin = form.admin.data

        app.db.session.add(user)
        app.db.session.commit()

    return flask.render_template('edit_accounts.html', form=form,
                                 __version__=app.config["VERSION"])


@app.route('/database/export')
def database_export_endpoint():
    filename = datetime.datetime.now().strftime("collegejump-export-%Y%m%d.zip")
    return flask.send_file(database.export_db(app.db),
                           attachment_filename=filename,
                           as_attachment=True,
                           mimetype='application/zip')


@app.route('/week/<int:week_number>')
def week_page(week_number):
    return flask.render_template('week_page.html',
                                 week_number=week_number,
                                 __version__=app.config["VERSION"])
