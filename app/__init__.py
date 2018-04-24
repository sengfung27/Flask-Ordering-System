from flask import Flask
#from instance.config import Config

app = Flask(__name__)
#app.config.from_object(Config)

from app import routes

app.run()


# tunnel the n execute flask_sqlalchemy