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

from pathlib import Path
import glob

from functions import videoFunc

from classes import Channel
from classes.Sec import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Begin Database Initialization
db.init_app(app)
db.app = app

#system.newLog(0, "Testing Stuff")

#vidList  =  RecordedVideo.RecordedVideo.query.order_by(RecordedVideo.RecordedVideo.videoDate.asc()).limit(10)

#for vid in vidList:
#    print(vid.videoDate) 

#if (current_user.id == recordedVid.owningUser or current_user.has_role('Admin') is True):



import shutil

fullDiskThreshold = 90 / 100

AGiG = 1024 * 1024 * 1024

total, used, free = shutil.disk_usage("/")

used = (AGiG*50)
print("Total: %d GiB" % (total // (2**30)))
print("Free : %d GiB" % (free // (2**30)))
print("Used : %d GiB" % (used // (2**30)))
print("")
print("Total: %d Bytes" % total)
print("Free : %d Bytes" % free)
print("Used : %d Bytes" % used)

Percentage = used / total
print("Percentage", Percentage)
print("fullDiskThreshold", fullDiskThreshold)

if Percentage > fullDiskThreshold:
    print("Full")
else:
    print("Not Full")

vidList  =  RecordedVideo.RecordedVideo.query.order_by(RecordedVideo.RecordedVideo.videoDate.asc()).limit(2)

for vid in vidList:
    print("Delete: " + str(vid.id) + " " + str(vid.videoDate) + " " + str(vid.channelName) + " owningUser =" + str(vid.owningUser ))
    
    #result = videoFunc.deleteVideo(vid.id)



