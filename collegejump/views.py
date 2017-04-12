import datetime
import flask
import flask_login
from collegejump.models import User
from collegejump import app, forms, models, database

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
        print("Attempting to log in {}... ".format(form.email.data), end="")
        email = form.email.data
        password = form.password.data

        user = models.User.load_user(email)
        if user and user.check_password(password):
            print("success!")
            # Modify the session so that the user is logged in.
            flask_login.login_user(user)

            # Redirect using the form utility. Use `?next=` if presented.
            return form.redirect()
        else:
            print("failure.")


    return flask.render_template('login.html', form=form,
                                 __version__=app.config["VERSION"])


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
        print("Attempting to create user... ", end="")
        user = User(form.email.data, form.password.data)
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
