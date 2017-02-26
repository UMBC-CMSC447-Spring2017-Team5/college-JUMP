from collegejump import app
import flask

@app.route('/')
@app.route('/index.html')
def front_page():
    return flask.render_template('index.html',
                                 VERSION=app.config["VERSION"])
    
@app.route('/calendar.html')
def calendar_page():
    return flask.render_template('calendar.html',
                                 VERSION=app.config["VERSION"], 
                                 gcal_link="dummylink")