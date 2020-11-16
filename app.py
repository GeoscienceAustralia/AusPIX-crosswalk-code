import logging
from flask import Flask
from controller import routes
import _conf
from pprint import pformat

app = Flask(__name__, template_folder=_conf.TEMPLATES_DIR, static_folder=_conf.STATIC_DIR)
app.register_blueprint(routes.routes)

logger = logging.getLogger('app')

# run the Flask app
if __name__ == '__main__':
    logging.basicConfig(filename=_conf.LOGFILE,
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')

    # Write all upper-case keys with string values in conf to log file
    logger.debug('conf = {}'.format(pformat({key: value
                                             for key, value in _conf.__dict__.items()
                                             if key == key.upper()
                                             and type(value) == str}
                                            )))

    # run the Flask app
    app.run(debug=_conf.DEBUG, threaded=True, use_reloader=False)