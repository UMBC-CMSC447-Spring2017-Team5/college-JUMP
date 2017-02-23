from collegejump import app
import flask

@app.route('/')
@app.route('/index.html')
def front_page():
    return flask.render_template('index.html',
                                 VERSION=app.config["VERSION"])
