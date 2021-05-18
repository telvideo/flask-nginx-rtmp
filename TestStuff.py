# -*- coding: UTF-8 -*-
#from gevent import monkey
#monkey.patch_all(thread=True)

from flask import request, flash, render_template, redirect, url_for, Blueprint, current_app, Response, session, abort
from flask_security import Security, SQLAlchemyUserDatastore, current_user, login_required, roles_required
from flask_security.utils import hash_password

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
from classes import settings

from globals import globalvars
from classes import RecordedVideo
import os

from pathlib import Path
import glob

from functions import videoFunc

from classes import Channel
from classes.Sec import User

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'redis'
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


from flask import Flask, render_template

def myfun():
    sysSettings = settings.settings.query.first()

#    sysSettings = settings.settings("Boggger!","","","",0,0,0,0,0,0,0,0,0,0,0,0)
    return(sysSettings)

app = Flask(__name__)

@app.route("/")
def index():
    pagetitle = "HomePage"
    return render_template("index.html",
                            mytitle=pagetitle,
                            mycontent="Hello World")
#render_template('admin.html',name= "Fred")
   
print("fred")

#fredSys=myfun()

myset = settings.getSettingsFromRedis()



import redis

r = redis.Redis(host=config.redisHost, port=config.redisPort, decode_responses=True)

#r = redis.StrictRedis(decode_responses=True)

myStr = "Fred String"
r.set('MARK TEST',str(myStr))
fred = str(r.get('MARK TEST'))


if fred == myStr:
    print("Yes")

r.delete("MARK TEST")
fred = r.get('MARK TEST')

exit()

recordedVid = RecordedVideo.RecordedVideo.query.filter_by(id=136).first()
recordedVid.NupVotes = recordedVid.NupVotes + 1 
print(recordedVid.NupVotes)
db.session.commit()
exit()

# This bit of code could be used to stop the hard drive over flowing maybe...
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



