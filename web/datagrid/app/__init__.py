from flask import Flask
import logging
from config import Config
# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.debug = True
app.config.from_object(Config)
# toolbar = DebugToolbarExtension(app)

# logging in terminal display (no log file)
logging.basicConfig(level=logging.DEBUG)

# logging to file
# logging.basicConfig(filename='log1.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

from app import routes #, models