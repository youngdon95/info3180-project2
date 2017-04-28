from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://wishlist:wishlist@localhost/wishlist"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://oawgfkqvwqevqc:3775af903db21f7e401d4a61d92164971db5348674c2b76ee631141ffa91154e@ec2-23-23-111-171.compute-1.amazonaws.com:5432/d3o1siuqllddm9"
DATABASE_URL=''
db = SQLAlchemy(app)
db.create_all()

from app import views,models
