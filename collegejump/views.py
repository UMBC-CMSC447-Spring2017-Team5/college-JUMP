from collegejump import app
import flask

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

@app.route('/login.html')
def login_page():
    return flask.render_template('login.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")
@app.route('/weekone.html')
def weekone_page():
    return flask.render_template('weekone.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")
@app.route('/weektwo.html')
def weektwo_page():
    return flask.render_template('weektwo.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")
@app.route('/weekthree.html')
def weekthree_page():
    return flask.render_template('weekthree.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")
@app.route('/weekfour.html')
def weekfour_page():
    return flask.render_template('weekfour.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")
@app.route('/weekfive.html')
def weekfive_page():
    return flask.render_template('weekfive.html',
                                 __version__=app.config["VERSION"],
                                 gcal_link="dummylink")
