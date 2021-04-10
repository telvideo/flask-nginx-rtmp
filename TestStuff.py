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

from globals import globalvars
from classes import RecordedVideo
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Begin Database Initialization
db.init_app(app)
db.app = app

#system.newLog(0, "Testing Stuff")

print("Testing Stuff")

#theUpvotes = upvotes.streamUpvotes.query.all()
#for upvote in theUpvotes:
#    db.session.delete(upvote) 

missingSet = set()

print(globalvars.videoRoot)

theVideos = RecordedVideo.RecordedVideo.query.all()

videos_root = globalvars.videoRoot + 'videos/'
for recordedVid in theVideos:
    filePath = videos_root + recordedVid.videoLocation

    if os.path.exists(filePath) == False:
        missingSet.add(recordedVid.id)

           # os.remove(filePath)
           # if os.path.exists(thumbnailPath):
           #     os.remove(thumbnailPath)
           # if os.path.exists(gifPath):
           #     os.remove(gifPath)

for theset in missingSet:
    print("ID = ")
    print(theset)

print(missingSet)
print("End")

#Last tester
