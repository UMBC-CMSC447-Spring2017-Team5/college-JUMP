import datetime
import flask
from flask import url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from collegejump import app
from collegejump import forms, models, database

@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)


@app.route('/')
def front_page():
    announcements = models.Announcement.query\
            .order_by(models.Announcement.timestamp.desc()).limit(10)
    return flask.render_template('index.html',
                                 announcements=announcements)


@app.route('/calendar')
def calendar_page():
    return flask.render_template('calendar.html', gcal_link="dummylink")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # If the login form is successfully POSTed to us here, try to log the user
    # in. Otherwise, render the page as normal.
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        try:
            user = models.User.query.filter_by(email=email).one()
            if user.check_password(password):
                # Modify the session so that the user is logged in.
                success = login_user(user)
                if success:
                    app.logger.info("Successful login by %r", user)
                    return form.redirect()
                else:
                    # If the login failed, here, it's not because of the
                    # password. Maybe the user is inactive?
                    app.logger.warning("Unexpected login failure by %r", user)
            else:
                app.logger.info("Wrong password for %r", user)

        except MultipleResultsFound:
            # This is actually really bad, and means the database is very broken.
            raise

        except NoResultFound:
            app.logger.info("Attempt to login with unknown email %r", email)

    return flask.render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return flask.redirect(flask.url_for('front_page'))

@app.route('/account_settings')
@login_required
def account_settings_page():
    return flask.render_template('account_settings.html')


@app.route('/announcement/new')
@app.route('/announcement/<int:announcement_id>/edit')
@login_required
def edit_announcement_page(announcement_id=None):
    if announcement_id is not None:
        announcement = models.Announcement.query\
                .filter(models.Announcement.id == announcement_id)\
                .one()
    else:
        announcement = models.Announcement(current_user.email, '', '')

    return flask.render_template('edit_announcement.html', announcement=announcement)

@app.route('/announcement/')
@app.route('/announcement/<int:announcement_id>')
def announcement_page(announcement_id=None):
    if announcement_id is not None:
        announcement = models.Announcement.query\
                .filter(models.Announcement.id == announcement_id)\
                .one()
        return flask.render_template('announcement.html', announcement=announcement)

    # Otherwise
    announcements = models.Announcement.query\
            .order_by(models.Announcement.timestamp.desc())
    return flask.render_template('all_announcements.html', announcements=announcements)


@app.route('/edit_accounts', methods=['GET', 'POST'])
#@login_required
def edit_accounts_page():
    # If the Create Acct form is successfully POSTed to us here, try to log the user
    # in. Otherwise, render the page as normal.
    form = forms.UserInfoForm()
    query = models.User.query.filter_by(email=form.email.data).first()

    if query is not None:
        if form.validate_on_submit():
            query.name = form.name.data
            query.email = form.email.data.lower()
            query.password = form.password.data
            query.admin = form.admin.data
            app.db.session.commit()
            app.logger.info("Updated  user %r in the database", query)
            return flask.redirect(flask.url_for('edit_accounts_page'))

    elif form.validate_on_submit():
        user = models.User(form.email.data.lower(), form.password.data)
        user.name = form.name.data
        user.admin = form.admin.data

        app.db.session.add(user)
        app.db.session.commit()

        app.logger.info("Created user %r in the database", user)

        return flask.redirect(flask.url_for('edit_accounts_page'))



    return flask.render_template('edit_accounts.html',
                                 form=form,
                                 users=models.User.query.all(),
                                 redirectto=url_for('edit_accounts_page'))



@app.route('/database/export')
@login_required
def database_export_endpoint():
    filename = datetime.datetime.now().strftime("collegejump-export-%Y%m%d.zip")
    return flask.send_file(database.export_db(),
                           attachment_filename=filename,
                           as_attachment=True,
                           mimetype='application/zip')


@app.route('/week/<int:week_number>')
def week_page(week_number):
    return flask.render_template('week_page.html',
                                 week_number=week_number)
