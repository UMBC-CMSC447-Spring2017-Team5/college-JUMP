import datetime
import flask
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from collegejump import app, forms, models, database, admin_required

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
    # Get the `returnto` or `next` query string.
    returnto = flask.request.args.get('returnto') \
            or flask.request.args.get('next')

    # Parse the form if it was given to us.
    form = forms.LoginForm()

    # If the form was submitted with returnto information, preserve it in case
    # we have to re-render the template.
    if form.returnto.data:
        returnto = form.returnto.data

    # If the login form is successfully POSTed to us here, try to log the user
    # in. Otherwise, render the page as normal.
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

    return flask.render_template('login.html', form=form, returnto=returnto)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return flask.redirect(flask.url_for('front_page'))

@app.route('/account_settings/<int:user_id>', methods=['GET', 'POST'])
@login_required
def account_settings_page(user_id):

    if not(current_user.id == user_id or current_user.admin):
        flask.abort(403)

    delete_form = forms.UserDeleteForm()
    form = forms.UserInfoForm()

    if delete_form.validate_on_submit():
        if delete_form.delete.data:
            # Retrieve the user for logging, then delete it.
            user = models.User.query.get(user_id)
            app.db.session.delete(user)
            app.db.session.commit()
            app.logger.info("Deleted user %r from the database", user)
            return flask.render_template('index.html')

    user = models.User.query.get(user_id)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data.lower()
        if form.password.data != "":
            user.password = form.password.data

        app.db.session.commit()
        app.logger.info("Updated user %r in the database", user)
        return flask.redirect(flask.url_for('account_settings_page',
                                            user_id=user_id))


    return flask.render_template('account_settings.html', user_id=user_id,
                                 user=user, form=form, deleteForm=delete_form)




@app.route('/announcement/new', methods=['GET', 'POST'])
@app.route('/announcement/<int:announcement_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_announcement_page(announcement_id=None):
    form = forms.AnnouncementForm()

    if announcement_id is not None:
        new_announcement = False
        announcement = models.Announcement.query.get(announcement_id)
    else:
        new_announcement = True
        announcement = models.Announcement(current_user.email, '', '')


    # If the form was submitted and valid, change the object and redirect to
    # viewing it.
    if form.validate_on_submit() and form.submit.data:
        # Update the announcement from the form if we're submitting finally.
        announcement.title = form.title.data
        announcement.content = form.content.data
        # If the announcement is brand new, add it to the session.
        if new_announcement:
            app.db.session.add(announcement)
        app.db.session.commit()
        return flask.redirect(flask.url_for('announcement_page', announcement_id=announcement.id))

    # Otherwise, if we're doing the GET method, fill the form with the original
    # data.
    elif flask.request.method == 'GET':
        form.title.data = announcement.title
        form.content.data = announcement.content

    return flask.render_template('edit_announcement.html',
                                 announcement_id=announcement.id,
                                 author=announcement.author,
                                 form=form)

@app.route('/announcement/')
@app.route('/announcement/<int:announcement_id>')
def announcement_page(announcement_id=None):
    if announcement_id is not None:
        announcement = models.Announcement.query.get(announcement_id)
        return flask.render_template('announcement.html', announcement=announcement)

    # Otherwise
    announcements = models.Announcement.query\
            .order_by(models.Announcement.timestamp.desc())
    return flask.render_template('all_announcements.html', announcements=announcements)


@app.route('/edit_accounts', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_accounts_page():
    form = forms.UserInfoForm()

    if form.validate_on_submit():
        user = form.to_user_model()

        app.db.session.add(user)
        app.db.session.commit()

        app.logger.info("Created user %r in the database", user)

        return flask.redirect(flask.url_for('edit_accounts_page'))

    return flask.render_template('edit_accounts.html', form=form,
                                 users=models.User.query.all())

@app.route('/setup', methods=['GET', 'POST'])
def setup_page():
    # If the SETUP_KEY isn't set in the config, it isn't first setup, and we
    # should just pretend this page doesn't exist.
    if 'SETUP_KEY' not in app.config:
        flask.abort(404)

    # Otherwise, continue trying to process the form. Checking of the SETUP_KEY
    # is handled by the form automagically.
    form = forms.FirstSetupUserInfoForm()
    if form.validate_on_submit():
        user = form.to_user_model()
        user.admin = True # A user created this way is always an admin

        app.db.session.add(user)
        app.db.session.commit()

        # Now that the user is created, log it and delete the SETUP_KEY.
        app.logger.info("Created user %r using SETUP_KEY, disabling SETUP_KEY", user)
        del app.config['SETUP_KEY']

        # Log the created user in automatically.
        login_user(user)

        return flask.redirect(flask.url_for("front_page"))

    # If the method was GET, pull `key` from the query parameters in to the
    # form, to get included in the subsequent POST automatically.
    if flask.request.method == 'GET':
        form.setup_key.data = flask.request.args.get('key')
        app.logger.debug("Filling setup form with key in query parameter: %r",
                         form.setup_key.data)

    # No matter what, check that what is now in the form parameter is correct,
    # otherwise, show them nothing.
    if form.setup_key.data != app.config['SETUP_KEY']:
        flask.abort(401) # unauthorized

    return flask.render_template('setup.html', form=form)

@app.route('/database/', methods=['GET', 'POST'])
@admin_required
def database_page():
    form = forms.DatabaseUploadForm()
    if form.validate_on_submit():
        # The data from the file is in bytes-like in form.zipfile.data, which we
        # pass to the import function.
        app.logger.info("Importing database from uploaded file by %r", current_user)
        try:
            database.import_db(form.zipfile.data)
            app.logger.info("Database import complete.")
            return flask.redirect(flask.url_for("front_page"))
        except DBAPIError:
            raise

    return flask.render_template('database.html', form=form)

@app.route('/database/export')
@admin_required
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
