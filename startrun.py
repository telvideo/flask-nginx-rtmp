# -*- coding: UTF-8 -*-
#from gevent import monkey
#monkey.patch_all(thread=True)

from flask import Flask
from conf import config

from classes import Stream
from classes import upvotes
from classes import comments
from classes import invites
from classes import webhook
from classes import subscriptions
from classes import notifications
from classes import stickers
from functions import database
from functions import system
from classes.shared import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Begin Database Initialization
db.init_app(app)
db.app = app

#delete all the stream upvotes
print("Start delete active streams")
theUpvotes = upvotes.streamUpvotes.query.all()
for upvote in theUpvotes:
    db.session.delete(upvote) 

#delete all the streams
theStream = Stream.Stream.query.all()
for stre in theStream:
    db.session.delete(stre)
db.session.commit()

system.newLog(0, "Startup Deleting Active Streams")

print("Deleted active streams")
