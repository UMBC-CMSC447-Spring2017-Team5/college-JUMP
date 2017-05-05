import datetime
import os
import flask
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from collegejump import app, forms, models, database, admin_required

@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)


@app.route('/', methods=["GET", "POST"])
def front_page():

    # If setup mode is happening, render a FirstSetupUserInfoForm.
    if 'SETUP_KEY' in app.config:
        setup_form = forms.FirstSetupUserInfoForm()
    else:
        setup_form = None


    if setup_form and setup_form.validate_on_submit():
        user = setup_form.to_user_model()
        user.admin = True # A user created this way is always an admin

        app.db.session.add(user)
        app.db.session.commit()

        # Now that the user is created, log it and delete the SETUP_KEY.
        app.logger.info("Created user %r using SETUP_KEY, disabling SETUP_KEY", user)
        del app.config['SETUP_KEY']

        # Log the created user in automatically.
        login_user(user)

        return flask.redirect(flask.url_for("front_page"))

    announcements = models.Announcement.query\
            .order_by(models.Announcement.timestamp.desc()).limit(10)
    return flask.render_template('index.html',
                                 announcements=announcements,
                                 setup_form=setup_form)


@app.route('/calendar')
def calendar_page():
    return flask.render_template('calendar.html', gcal_link="dummylink")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Get the `returnto` or `next` query string, otherwise leave blank.
    returnto = flask.request.args.get('returnto') \
            or flask.request.args.get('next') \
            or ''

    # Create the form object with its defaults. If a `returnto` was submitted,
    # it will be preserved here.
    form = forms.LoginForm(returnto=returnto)

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
                    flask.flash('Login successful.', 'success')
                    return form.redirect()
                else:
                    # If the login failed here, it's not because of the
                    # password. Maybe the user is inactive?
                    app.logger.warning("Unexpected login failure by %r", user)
            else:
                app.logger.info("Wrong password for %r", user)

        except MultipleResultsFound:
            # This is actually really bad, and means the database is very broken.
            app.logger.error("Multiple results found on what should be unique email %r", email)

        except NoResultFound:
            app.logger.info("Attempt to login with unknown email %r", email)

        flask.flash('Login failed.', 'error')

    return flask.render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return flask.redirect(flask.url_for('front_page'))

@app.route('/account/<int:user_id>', methods=['GET', 'POST'])
@login_required
def account_settings_page(user_id):
    # Load the user up here before we process the form so that we can use it to
    user = models.User.query.get(user_id)

    # Unless the user is editing their own account, or is an admin, deny
    # access. If the user is an admin, serve them a complete form with more
    # fields, otherwise, give them a limited form.
    if current_user.admin:
        # Populate semester data in the form. This is separate from the initializer
        # because it requires a database query.
        form = forms.UserInfoAdminForm(name=user.name,
                                       email=user.email,
                                       admin=user.admin,
                                       semesters_enrolled=[s.id for s in user.semesters])
        form.populate_semesters()

    elif current_user.id == user_id:
        form = forms.UserInfoForm(name=user.name)
    else:
        return flask.abort(403)

    # We check if the user is to be deleted. For this, we don't yet validate the
    # form, because not all of the fields need to be valid.
    if flask.request.method == 'POST' \
            and isinstance(form, forms.UserInfoAdminForm) \
            and form.delete.data:
        # Retrieve the user for logging, then delete it.
        app.db.session.delete(user)
        app.db.session.commit()
        app.logger.info("Deleted user %r from the database", user)
        flask.flash("Deleted user '{}'".format(user.email), 'success')
        return flask.redirect(flask.url_for('front_page'))

    # Otherwise, we update the user information.
    if form.validate_on_submit():
        user.name = form.name.data
        if form.password.data: # non-None, non-empty
            user.password = form.password.data

        if isinstance(form, forms.UserInfoAdminForm):
            user.email = form.email.data.lower()
            user.admin = form.admin.data
            user.semesters = list(form.get_semesters_enrolled())

        app.db.session.commit()
        app.logger.info("Updated user %r", user)
        flask.flash("Updated user '{}'".format(user.email))
        return flask.redirect(flask.url_for('account_settings_page',
                                            user_id=user_id))

    return flask.render_template('account_settings.html', user=user, form=form)

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
            flask.flash('Announcement posted successfully!', 'success')
            app.db.session.add(announcement)
        else:
            flask.flash('Announcement updated successfully!', 'success')
        app.db.session.commit()
        return flask.redirect(flask.url_for('front_page'))

    # Otherwise, if we're doing the GET method, fill the form with the original
    # data.
    elif flask.request.method == 'GET':
        form.title.data = announcement.title
        form.content.data = announcement.content

    return flask.render_template('edit_announcement.html',
                                 announcement_id=announcement.id,
                                 author=announcement.author,
                                 form=form)

@app.route('/syllabus/', methods=["GET", "POST"])
@admin_required
def syllabus_page():
    form = forms.SemesterForm()
    if form.validate_on_submit():
        semester = models.Semester(form.name.data, form.order.data)
        app.db.session.add(semester)
        app.db.session.commit()

        return flask.redirect(flask.url_for('syllabus_page'))

    all_semesters = models.Semester.query.order_by('order')
    return flask.render_template("syllabus_root.html", all_semesters=all_semesters, form=form)

@app.route('/syllabus/semester/<int:semester_id>', methods=["GET", "POST"])
@admin_required
def edit_semester_page(semester_id):
    """Edit the syllabus for a whole semester."""
    # pylint: disable=no-member
    # Look the semester up by id, eagerly loading the weeks, so they can be
    # displayed or changed without firing a bunch of extra queries.
    semester = models.Semester.query\
            .options(joinedload(models.Semester.weeks)) \
            .get(semester_id)

    semester_form = forms.SemesterForm(name=semester.name,
                                       order=semester.order)
    week_form = forms.WeekForm()

    # If the delete button is pressed on the semester, delete it without
    # validating the rest of the input.
    if flask.request.method == 'POST' and semester_form.delete.data:
        app.logger.info("Deleting %r", semester)
        app.db.session.delete(semester)
        app.db.session.commit()
        flask.flash("Deleted semester '{}'".format(semester.name), 'success')
        return flask.redirect(flask.url_for('syllabus_page'))

    # If POSTing a valid semester form, apply the changes.
    if semester_form.validate_on_submit():
        semester.name = semester_form.name.data
        semester.order = semester_form.order.data

        # Commit at the end of processing the database.
        app.db.session.commit()

        # Redirect, so the page is loaded again by GET with changes made.
        flask.flash("Updated semester '{}'".format(semester.name), 'success')
        return flask.redirect(flask.url_for('edit_semester_page', semester_id=semester.id))

    # If POSTing a valid new week, create it and attach it to this semester as
    # the last week.
    if week_form.validate_on_submit():
        week = models.Week(semester_id, len(semester.weeks) + 1,
                           week_form.header.data,
                           week_form.intro.data)
        app.logger.debug("Creating new week %r", week)
        app.db.session.add(week)
        app.db.session.commit()
        app.logger.info("Creating %r", week)
        flask.flash("Created week {} in semester '{}'".format(week.week_num, semester.name),
                    'success')
        return flask.redirect(flask.url_for('edit_semester_page', semester_id=semester.id))

    return flask.render_template("semester.html",
                                 semester=semester,
                                 semester_form=semester_form,
                                 week_form=week_form)

@app.route('/syllabus/semester/<int:semester_id>/week/<int:week_num>', methods=["GET", "POST"])
@admin_required
def edit_week_page(semester_id, week_num):
    """Edit a particular week in a semester."""
    form = forms.WeekForm()

    # We aren't given the week ID, just the semester ID and week number, so we
    # look it up by those. The database guarantees that the pair is unique.
    week = models.Week.query.filter_by(semester_id=semester_id,
                                       week_num=week_num).one()

    # If the form was submitted, validate it and update the week data from it.
    if form.validate_on_submit() and form.submit.data is True:
        app.logger.debug("Updating week %r from form", week)
        week.header = form.header.data
        week.intro = form.intro.data

        # If a file was uploaded, extract it into a Document, store that, and
        # associate it with this week.
        if form.new_document.has_file():
            app.logger.debug("Adding document to week %r", week)
            # Create the Document object using the form data.
            document = models.Document(os.path.basename(form.new_document.data.filename),
                                       form.new_document.data.stream.read())

            # Add the Document to the current session.
            app.db.session.add(document)

            # Associate the document with the week. The ORM will handle the
            # rest.
            week.documents.append(document)

        # Flush the changes to the session.
        app.db.session.commit()

        # If we submitted everything correctly, redirect to this page again to
        # refresh the form and all the data.
        return flask.redirect(flask.url_for('edit_week_page',
                                            semester_id=semester_id,
                                            week_num=week_num))

    # We reach this point on GET or on unsuccessful POST. Ensure the form is
    # pre-filled with data if it's blank, (otherwise preserve data) and then
    # render everything.
    form.header.data = form.header.data or week.header
    form.intro.data = form.intro.data or week.intro

    return flask.render_template('edit_week.html',
                                 week=week,
                                 form=form,
                                 show_edit_options=True)

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


@app.route('/account/all', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_accounts_page():
    form = forms.UserInfoAdminForm()

    if form.validate_on_submit():
        user = form.to_user_model()

        app.db.session.add(user)
        app.db.session.commit()

        app.logger.info("Created user %r in the database", user)

        return flask.redirect(flask.url_for('edit_accounts_page'))

    return flask.render_template('edit_accounts.html', form=form,
                                 users=models.User.query.all())

@app.route('/document/<int:document_id>')
@login_required
def document_page(document_id):
    document = models.Document.query.get(document_id)
    return flask.send_file(document.data, attachment_filename=document.name)

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
