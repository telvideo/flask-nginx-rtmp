# -*- coding: UTF-8 -*-
#from gevent import monkey
#monkey.patch_all(thread=True)

from flask import request, flash, render_template, redirect, url_for, Blueprint, current_app, Response, session, abort
from flask_security import Security, SQLAlchemyUserDatastore, current_user, login_required, roles_required
from flask_security.utils import hash_password
from sqlalchemy.sql import text

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
from classes import topics

from globals import globalvars
from classes import RecordedVideo
import os

from pathlib import Path
import glob

from functions import videoFunc

from classes import Channel
from classes import Sec

import jinja2
    
mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=mtemplateLoader)
#sideBartemplate = templateEnv.get_template("/templates/redissidebar.html")
#caroueltemplate = templateEnv.get_template("/templates/rediscarousel")
#liveNowtemplate = templateEnv.get_template("/templates/redisliveNow.html")


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
import redis
from flask_redis import FlaskRedis
   
print("fred")



stri ="{} {}\n".format("videos_root",  "aClip.gifLocation")

f = open("/opt/dicks.txt", "a")
f.write(stri)
f.close()

settings.setupRedis(app) # Boggs needs to password this!

from classes.settings import r

from flask_socketio import emit
from classes.shared import db, socketio

#myset = settings.getSettingsFromRedis()
#r = redis.Redis(host=config.redisHost, port=config.redisPort, decode_responses=True)
#r = FlaskRedis(decode_responses=True)
import time

from pottery import Redlock
#redis_lock = Redlock(key='OSP_DB_INIT_HANDLER', masters={r})
#redis_lock.acquire()
from functions import templateFilters
from functions import themes



userID = int(1)

if True:
    chans = Channel.Channel.query.join(Sec.User,Sec.User.id == userID).with_entities(
        Channel.Channel.protected,
        Channel.Channel.Nsubscriptions,
        Channel.Channel.views,
        Channel.Channel.channelName,
        Channel.Channel.imageLocation,
        Channel.Channel.owningUser,
        Channel.Channel.description,
        Channel.Channel.topic,
        Channel.Channel.id,
        Sec.User.username,
        Sec.User.pictureLocation,
        Channel.Channel.id).filter(Channel.Channel.owningUser == userID).all()

    openStreams = Stream.Stream.query\
        .join(Channel.Channel,Channel.Channel.id == Stream.Stream.linkedChannel)\
        .join(Sec.User, Sec.User.id == userID ).with_entities(
            Channel.Channel.channelLoc,
            Channel.Channel.protected,
            #Channel.Channel.id,
            Channel.Channel.id.label('chanID'),
            Channel.Channel.channelName,
            Stream.Stream.streamName,
            Stream.Stream.topic,
            Stream.Stream.NupVotes,
            Stream.Stream.currentViewers,
            Stream.Stream.totalViewers).all()

    userChannels = []
    strSet = set()
    for stre in openStreams:
        strSet.add(stre.id)

    for chan in chans:
        if chan.id in openStreams:
            isStreaming = True
        else:
            isStreaming = False
            
        channelData = {"protected":chan.protected,
            "id":chan.id,
            "owningUser":chan.owningUser,
            "Nsubscriptions":chan.Nsubscriptions,
            "views":chan.views,
            "imageLocation":chan.imageLocation,
            "channelName":chan.channelName,
            "username":chan.username,
            "isStreaming":isStreaming,
            "pictureLocation":chan.pictureLocation,
            "description":chan.description
            }
        
        userChannels.append(channelData)


    recordedVideoQuery = []
    clipsList = []
    streams = []
    streamerQuery = Sec.User.query.filter_by(id=userID).first()
    
    #return render_template(themes.checkOverride('videoListView.html'), openStreams=streams, recordedVids=recordedVideoQuery, userChannels=userChannels, clipsList=clipsList, title=streamerQuery.username, streamerData=streamerQuery)

    streamerQuery = Sec.User.query.filter_by(id=userID).first()
    if streamerQuery is not None:
        if streamerQuery.has_role('Streamer'):
            userChannels = Channel.Channel.query.filter_by(owningUser=userID).all()

            streams = []

            for channel in userChannels:
                for stream in channel.stream:
                    streams.append(stream)

            recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(owningUser=userID, pending=False, published=True).all()

            # Sort Video to Show Newest First
            recordedVideoQuery.sort(key=lambda x: x.videoDate, reverse=True)

            clipsList = []
            for vid in recordedVideoQuery:
                for clip in vid.clips:
                    if clip.published is True:
                        clipsList.append(clip)

            clipsList.sort(key=lambda x: x.views, reverse=True)

   #         return render_template(themes.checkOverride('videoListView.html'), openStreams=streams, recordedVids=recordedVideoQuery, userChannels=userChannels, clipsList=clipsList, title=streamerQuery.username, streamerData=streamerQuery)
    flash('Invalid Streamer','error')
   # return redirect(url_for("root.main_page"))


exit()

recordedVids = RecordedVideo.RecordedVideo.query.filter_by(channelID=chanID, pending=False, published=True)\
            .join(Sec.User,Sec.User.id == RecordedVideo.RecordedVideo.owningUser)\
            .join(Channel.Channel, Channel.Channel.id == chanID)\
            .with_entities(
            Channel.Channel.protected,
            RecordedVideo.RecordedVideo.id,
            RecordedVideo.RecordedVideo.gifLocation,
#            RecordedVideo.RecordedVideo.
            RecordedVideo.RecordedVideo.topic,
            RecordedVideo.RecordedVideo.videoDate,
            RecordedVideo.RecordedVideo.published).order_by(RecordedVideo.RecordedVideo. videoDate.desc()).all()



recordedVids = RecordedVideo.RecordedVideo.query.filter_by(channelID=chanID, pending=False, published=True).order_by(
        RecordedVideo.RecordedVideo. videoDate.desc()).all()

rec  = recordedVids[0]
chan = recordedVids[0].channel
cid  = recordedVids[0].channel.id      #
bob = recordedVids[0].user.username
       

exit()
sysSettings = settings.getSettingsFromRedis()
#doCarouel = bool(reqestType['doCarouel'])

sideBarliveView = r.get('sideBarliveView')

# if there is nothing in redis we need to get it and set it for everyone else
if (True ):
    streamQuery = Stream.Stream.query.join(Channel.Channel, Channel.Channel.id == Stream.Stream.linkedChannel) \
    .join(Sec.User, Sec.User.id == Channel.Channel.owningUser) \
    .join(topics.topics, topics.topics.id == Stream.Stream.topic ).with_entities(Stream.Stream.id,
        Stream.Stream.linkedChannel,
        Stream.Stream.streamName,
        Stream.Stream.topic,
        topics.topics.name,
        Stream.Stream.currentViewers,
        Stream.Stream.totalViewers,
        Stream.Stream.NupVotes,
        Channel.Channel.channelLoc,
        Channel.Channel.protected,
        Sec.User.pictureLocation,
#        Sec.User.verified,
#        Channel.Channel.imageLocation,
        Sec.User.username,
#        Channel.Channel.channelName
        ).order_by(Stream.Stream.currentViewers.desc()).all()
    
    sysSettings = settings.getSettingsFromRedis()

    mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=mtemplateLoader)
    templateFilters.init(templateEnv)

    sideBartemplate = templateEnv.get_template(themes.checkOverrideDirect('redissidebar.html',sysSettings.systemTheme))
    caroueltemplate = templateEnv.get_template(themes.checkOverrideDirect('rediscarousel.html',sysSettings.systemTheme))
    liveNowtemplate = templateEnv.get_template(themes.checkOverrideDirect('redisliveNow.html',sysSettings.systemTheme))

    sideBarliveView = sideBartemplate.render(sideBarStreamList = streamQuery)  
    carouselliveView = caroueltemplate.render(sideBarStreamList = streamQuery)  
    liveNowView      = liveNowtemplate.render(sideBarStreamList = streamQuery, sysSettingsprotected = sysSettings.protectionEnabled)  

exit()
channelID = 2

if True:
#    channelID = str(streamData['data'])
    channelID = 2 #str(streamData['channelID'])
 
    sysSettings = settings.getSettingsFromRedis()


    requestedChannel = Channel.Channel.query.filter_by(id=channelID).first()
    stream = Stream.Stream.query.filter_by(linkedChannel=channelID).first()

    currentViewers = 555 #xmpp.getChannelCounts(requestedChannel.channelLoc)

    streamName = ""
    streamTopic = 0

    requestedChannel.currentViewers = currentViewers
#    db.session.commit()

    if stream is not None:
        stream.currentViewers = currentViewers
#        db.session.commit()
        streamName = stream.streamName
        streamTopic = stream.topic

    else:
        streamName = requestedChannel.channelName
        streamTopic = requestedChannel.topic

    if requestedChannel.imageLocation is None:
        channelImage = (sysSettings.siteProtocol + sysSettings.siteAddress + "/static/img/video-placeholder.jpg")
    else:
        channelImage = (sysSettings.siteProtocol + sysSettings.siteAddress + "/images/" + requestedChannel.imageLocation)

    join_room(equestedChannel.channelLoc)
   
 
    if current_user.is_authenticated:
        pictureLocation = current_user.pictureLocation
        if current_user.pictureLocation is None:
            pictureLocation = '/static/img/user2.png'
        else:
            pictureLocation = '/images/' + pictureLocation

        webhookFunc.runWebhook(requestedChannel.id, 2, channelname=requestedChannel.channelName,
                   channelurl=(sysSettings.siteProtocol + sysSettings.siteAddress + "/channel/" + str(requestedChannel.id)),
                   channeltopic=requestedChannel.topic, channelimage=channelImage, streamer=templateFilters.get_userName(requestedChannel.owningUser),
                   channeldescription=str(requestedChannel.description), streamname=streamName, streamurl=(sysSettings.siteProtocol + sysSettings.siteAddress + "/view/" + requestedChannel.channelLoc),
                   streamtopic=templateFilters.get_topicName(streamTopic), streamimage=(sysSettings.siteProtocol + sysSettings.siteAddress + "/stream-thumb/" + requestedChannel.channelLoc + ".png"),
                   user=current_user.username, userpicture=(sysSettings.siteProtocol + sysSettings.siteAddress + str(pictureLocation)))
    else:
        webhookFunc.runWebhook(requestedChannel.id, 2, channelname=requestedChannel.channelName,
                   channelurl=(sysSettings.siteProtocol + sysSettings.siteAddress + "/channel/" + str(requestedChannel.id)),
                   channeltopic=requestedChannel.topic, channelimage=channelImage, streamer=templateFilters.get_userName(requestedChannel.owningUser),
                   channeldescription=str(requestedChannel.description), streamname=streamName,
                   streamurl=(sysSettings.siteProtocol + sysSettings.siteAddress + "/view/" + requestedChannel.channelLoc),
                   streamtopic=templateFilters.get_topicName(streamTopic), streamimage=(sysSettings.siteProtocol + sysSettings.siteAddress + "/stream-thumb/" + requestedChannel.channelLoc + ".png"),
                   user="Guest", userpicture=(sysSettings.siteProtocol + sysSettings.siteAddress + '/static/img/user2.png'))

 
 #   db.session.commit()
 #   db.session.close()

###
  #  requestedChannel = Channel.Channel.query.filter_by(channelLoc=channelLoc).first()
  #  streamData = Stream.Stream.query.filter_by(streamKey=requestedChannel.streamKey).first()

    requestedChannel.views = requestedChannel.views + 1
    if stream is not None:
       stream.totalViewers = stream.totalViewers + 1
#    db.session.commit()

    newView = views.views(0, requestedChannel.id)
    db.session.add(newView)

    try:
        db.session.commit()
    except: 
        pass
        
    db.session.close()







   
exit()

print("BOB")

doCarouel = True #bool(reqestType['doCarouel'])

sideBarliveView = r.get('sideBarliveView')

# if there is nothing in redis we need to set it
if (True):
    print("sideBarliveViewString = None")

    #r.delete("MARK TEST")    #fred = r.get('MARK TEST')
    channelID =2
    #  streamQuery = Stream.Stream.query.order_by(Stream.Stream.currentViewers).all()
 
    streamQuery = Stream.Stream.query.join(Channel.Channel, Channel.Channel.id == Stream.Stream.linkedChannel) \
        .filter_by(id=channelID).with_entities(Stream.Stream.id,
            Stream.Stream.topic,
            Stream.Stream.streamName,
            Stream.Stream.currentViewers,
            Stream.Stream.totalViewers,
            Stream.Stream.startTimestamp,
            Stream.Stream.NupVotes,
            Channel.Channel.views,
            Channel.Channel.Nsubscriptions        
            ).first()

    # if the stream query failed it's cos there is no stream linked to the channel so get the channel info
    if streamQuery == None:
        requestedChannel = Channel.Channel.query.filter_by(id=channelID).with_entities(Channel.Channel.views,
            #Channel.Channel.currentViewers,
            Channel.Channel.Nsubscriptions).first() 
        views = requestedChannel.views
        Nsubscriptions = requestedChannel.Nsubscriptions
    else:
        views = streamQuery.views
        Nsubscriptions = streamQuery.Nsubscriptions


    if streamQuery != None:
        try:
            viewers = 0#xmpp.getChannelCounts(channelLoc)
        except: 
            viewers = 0

        streamData = {"streamName":streamQuery.streamName,
                "streamTime":str(streamQuery.startTimestamp),
                "topic"     :streamQuery.topic,
                "viewers"   :viewers,
                "NupVotes"  :str(streamQuery.NupVotes),
                "views"     :str(views)}
    else:
        streamData = {"streamName":"",
                "streamTime":"",
                "topic"     :-1,
                "viewers"   :'0',
                "NupVotes"  :'0',
                "views"     :str(views)}

    gname = streamQuery.streamName

    #channelLoc    = str("b51c0492-8986-4005-ac10-d1a6e565c8be")
    channelID = 2
 

    streamQuery = None
    myRedisID = "streamName" +str(channelID)
    #r.delete(myRedisID)

    streamData = r.hgetall(myRedisID)
    # if there is nothing in redis we need to get it and set it for everyone else to get later
    if (streamData == {}):
        streamQuery = Stream.Stream.query.filter_by(linkedChannel=channelID) \
            .with_entities(Stream.Stream.streamName, Stream.Stream.topic, Stream.Stream.startTimestamp). first()

        if streamQuery != None:
            streamData = {"streamName":streamQuery.streamName,
                    "streamTime":str(streamQuery.startTimestamp),
                    "topic"     :streamQuery.topic}
        else:
            streamData = {"streamName":"",
                    "streamTime":"",
                    "topic"     :""}

        r.hmset(myRedisID,streamData)    # set redis even if there is no stream...                            
        r.expire(myRedisID, 30)           # after 5 seconds it will die and can be recreated

    nStream = r.hgetall(myRedisID)

    # if the redis or the database says there is a stream tell the user about it.
    if ( streamQuery != None) or (streamData["topic"]!=""):
        exit()

        emit('getStreamStuffResponse', {'streamName' : streamData["streamName"],
                                                'streamTopic': streamData["topic"],
                                                'startTimestamp': streamData["streamTime"]})

    exit()
    sysSettings = settings.getSettingsFromRedis()

    sideBarliveView = sideBartemplate.render(sideBarStreamList = streamQuery)  
    carouselliveView = caroueltemplate.render(sideBarStreamList = streamQuery)  
    liveNowView      = liveNowtemplate.render(sideBarStreamList = streamQuery, sysSettingsprotected = sysSettings.protectionEnabled)  

    r.set('carouselliveView',carouselliveView) 
    r.set('liveNowView',liveNowView) 
    r.set('sideBarliveView',sideBarliveView) #set this one last...
    r.expire('sideBarliveView', 30)
else:
    # sideBarliveView is already set, so get the others if they are wanted
    if (doCarouel == True):
        carouselliveView = r.get('carouselliveView')
        liveNowView = r.get('liveNowView')
    else:
        carouselliveView = ""
        liveNowView = ""

#    r.get('carouselliveView',carouselliveView) 
#    r.get('liveNowView',liveNowView) 

print("End.")
#emit('getViewerStuffResponse', {'data': str(carouselliveView),'sideBarStreamList': str(sideBarliveView),'liveNowList': str(liveNowView)})

exit()

#userID = 3
#theText ="New Set Value!!!"
#cmd = 'UPDATE user SET donationURL = :theText  WHERE id = :userID'

#result = db.engine.execute(text(cmd), theText = theText, userID = userID)

#system.newLog(1, "User "  + current_user.username +" AFTER*********** " + str(userID) + " to " + theText)



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






