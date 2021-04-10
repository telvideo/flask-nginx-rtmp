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

from classes import Channel
from classes.Sec import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Begin Database Initialization
db.init_app(app)
db.app = app

system.newLog(0, "RUNNING OSP UNUSED FILE TRIMMER")

print("--------------------------------------------------------------------------")
print("OSP UNUSED FILE TRIMMER")
print("--------------------------------------------------------------------------")

videos_root   = globalvars.videoRoot + 'videos/'
images_root   = globalvars.videoRoot + 'images/'
stickers_root = globalvars.videoRoot + 'images/stickers/'

print("globalvars.videoRoot : " + globalvars.videoRoot)
print("videos_root          : " + videos_root)
print("images_root          : " + images_root)
print("stickers_root        : " + stickers_root)
print("--------------------------------------------------------------------------")

fileNameSet = set()

#print("Channel")
theChannels = Channel.Channel.query.all()
for theChan in theChannels:
    fileNameSet.add("{}{}".format(images_root, theChan.imageLocation))
    fileNameSet.add("{}{}".format(images_root, theChan.offlineImageLocation))
    
#print("Clips")
theClips = RecordedVideo.Clips.query.all()
for aClip in theClips:
    fileNameSet.add("{}{}".format(videos_root,  aClip.videoLocation))
    fileNameSet.add("{}{}".format(videos_root,  aClip.thumbnailLocation))
    fileNameSet.add("{}{}".format(videos_root,  aClip.gifLocation))

#print("RecordedVideo")
theVideos = RecordedVideo.RecordedVideo.query.all()
for recordedVid in theVideos:
    fileNameSet.add("{}{}".format(videos_root,  recordedVid.videoLocation))
    fileNameSet.add("{}{}".format(videos_root,  recordedVid.thumbnailLocation))
    fileNameSet.add("{}{}".format(videos_root,  recordedVid.gifLocation))

#print("Stickers")
theStickers = stickers.stickers.query.all()
for aSticker in theStickers:
    fileNameSet.add(stickers_root + aSticker.filename)

#print("User")
theUsers = User.query.all()
for aUser in theUsers:
    fileNameSet.add("{}{}".format(images_root, aUser.pictureLocation))

# we might have added these previously when we did not check each one when adding, but it's faster like this
fileNameSet.discard("{}{}".format(videos_root,"None"))
fileNameSet.discard("{}{}".format(images_root,"None"))
fileNameSet.discard("{}{}".format(stickers_root,"None"))

fileList =list()

for r,d,f in os.walk(images_root):    # walk through dir trees getting all files we might need to delete 
    for i in f: 
        fileList.append( os.path.join(r,i))

for r,d,f in os.walk(videos_root):  
    for i in f: 
        fileList.append( os.path.join(r,i))

#for theList in fileList:
#   print(theList)

foundFiles = 0
notfoundFiles = 0

for fileName in fileList:
    if fileName in fileNameSet:
        foundFiles += 1
    else:
        print(fileName)
        notfoundFiles += 1
print("--------------------------------------------------------------------------")
print(notfoundFiles , "Files do not have links in OSP database.")
print(foundFiles , "Files have links in OSP database.")

#missingFiles = 0 
#for fFile in fileNameSet:
#    if fFile not in fileList:
#        missingFiles +=1

#print(str(missingFiles) + " Database links are missing files on hard drive ")   
print("--------------------------------------------------------------------------")

question = input("Type: BOGGS and press enter if you really do want to delete the files from hard drive which do not have links in the OSP database? ")
if question == "BOGGS":
    for fileName in fileList:
        if fileName not in fileNameSet:
            if os.path.exists(fileName):
                os.remove(fileName)
                print("Deleted " + fileName)
                system.newLog(0, "Admin Deleted unused " + fileName)
else:
    print("You did not type BOGGS. No files were deleted (Chicken).")

print("Bye!")
