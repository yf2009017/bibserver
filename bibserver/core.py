import os, requests, json
from flask import Flask

from bibserver import default_settings
from flask.ext.login import LoginManager, current_user

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    configure_app(app)
    initialise_index(app)
    setup_error_email(app)
    login_manager.setup_app(app)
    return app

def configure_app(app):
    app.config.from_object(default_settings)
    # parent directory
    here = os.path.dirname(os.path.abspath( __file__ ))
    config_path = os.path.join(os.path.dirname(here), 'app.cfg')
    if os.path.exists(config_path):
        app.config.from_pyfile(config_path)

def initialise_index(app):
    if app.config['INITIALISE_INDEX']:
        mappings = app.config["MAPPINGS"]
        i = 'http://' + str(app.config['ELASTIC_SEARCH_HOST']).lstrip('http://').rstrip('/')
        i += '/' + app.config['ELASTIC_SEARCH_DB']
        for key, mapping in mappings.iteritems():
            im = i + '/' + key + '/_mapping'
            exists = requests.get(im)
            if exists.status_code != 200:
                ri = requests.post(i)
                r = requests.put(im, json.dumps(mapping))
                print key, r.status_code


def setup_error_email(app):
    ADMINS = app.config.get('ADMINS', '')
    if not app.debug and ADMINS:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@no-reply.com',
                                   ADMINS, 'error')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

app = create_app()

