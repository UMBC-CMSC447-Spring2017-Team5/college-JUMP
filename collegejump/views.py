from collegejump import app
import flask

@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)

@app.route('/')
@app.route('/index.html')
def front_page():
    return flask.render_template('index.html',
                                 __version__=app.config["VERSION"])
    
@app.route('/calendar.html')
def calendar_page():
    return flask.render_template('calendar.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")

@app.route('/login.html')
def login_page():
    return flask.render_template('login.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")