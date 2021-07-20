from flask_socketio import emit
from flask_security import current_user
from sqlalchemy import update
from flask import render_template
from classes.shared import db, socketio
from classes import Channel
from classes import Stream
from classes import settings
from classes import Sec
from classes import topics

from functions import system
from functions import webhookFunc
from functions import templateFilters
from functions import xmpp
from functions import themes

from classes.settings import r

import jinja2
    
mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=mtemplateLoader)
sideBartemplate = templateEnv.get_template("/templates/liveStreams.html")
caroueltemplate = templateEnv.get_template("/templates/carousel.html")
liveNowtemplate = templateEnv.get_template("/templates/liveNow.html")

@socketio.on('getViewerStuff')
def handle_viewer_Stuff(reqestType):

    doCarouel = bool(reqestType['doCarouel'])

    sideBarliveView = r.get('sideBarliveView')

    # if there is nothing in redis we need to get it and set it for everyone else
    if (sideBarliveView == None):
        #print("sideBarliveViewString = None")

        #r.delete("MARK TEST")    #fred = r.get('MARK TEST')
        
        #  streamQuery = Stream.Stream.query.order_by(Stream.Stream.currentViewers).all()
        streamQuery = Stream.Stream.query.join(Channel.Channel, Channel.Channel.id == Stream.Stream.linkedChannel) \
        .join(Sec.User, Sec.User.id == Channel.Channel.owningUser) \
        .join(topics.topics, topics.topics.id == Stream.Stream.topic ).with_entities(Stream.Stream.id,
            Stream.Stream.linkedChannel,
            Stream.Stream.streamName,
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

        sideBarliveView = sideBartemplate.render(sideBarStreamList = streamQuery)  
        carouselliveView = caroueltemplate.render(sideBarStreamList = streamQuery)  
        liveNowView      = liveNowtemplate.render(sideBarStreamList = streamQuery, sysSettingsprotected = sysSettings.protectionEnabled)  

        r.set('sideBarliveView',sideBarliveView)
        r.expire('sideBarliveView', 7)  # timeout for redis, this must be 1 less than the timeout used when the UI calls this 

        r.set('carouselliveView',carouselliveView) 
        r.set('liveNowView',liveNowView) 
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

#    carouselliveView = "From1"
#    liveNowView = "From2"
#    sideBarliveView ="From3 "

    emit('getViewerStuffResponse', {'data': str(carouselliveView),'sideBarStreamList': str(sideBarliveView),'liveNowList': str(liveNowView)})

    return 'OK'

#####    
    doCarouel = bool(reqestType['doCarouel'])
#    doCarouel = False

    # chanSubQuery = subscriptions.channelSubs.query.filter_by(userID=current_user.id).all()
    # chanSubQuery = []

 #   if current_user.is_authenticated:
 #       chanSubQuery = subscriptions.channelSubs.query.filter_by(userID=current_user.id).\
 #           join(Channel.Channel, Channel.Channel.id == subscriptions.channelSubs.channelID ).\
 #           with_entities(Channel.Channel.imageLocation,Channel.Channel.id,Channel.Channel.channelName)

    
    #  streamQuery = Stream.Stream.query.order_by(Stream.Stream.currentViewers).all()
    streamQuery = Stream.Stream.query.join(Channel.Channel, Channel.Channel.id == Stream.Stream.linkedChannel) \
    .join(Sec.User, Sec.User.id == Channel.Channel.owningUser) \
    .join(topics.topics, topics.topics.id == Stream.Stream.topic ).with_entities(Stream.Stream.id,
#        Stream.Stream.uuid,
#        Stream.Stream.startTimestamp,
        Stream.Stream.linkedChannel,
#        Stream.Stream.streamKey,
        Stream.Stream.streamName,
        topics.topics.name,
        Stream.Stream.currentViewers,
        Stream.Stream.totalViewers,
#        Stream.Stream.rtmpServer,
        Stream.Stream.NupVotes,
        Channel.Channel.channelLoc,
        Channel.Channel.protected,
        Sec.User.pictureLocation,
#        Sec.User.verified,
#        Channel.Channel.imageLocation,
        Sec.User.username,
#        Channel.Channel.channelName
        ).order_by(Stream.Stream.currentViewers.desc()).all()
   
    
    streamliveView = sideBartemplate.render(sideBarStreamList = streamQuery)  

    # if this is the main page render the carousel and live now
    if (doCarouel is True): 
        sysSettings = settings.getSettingsFromRedis()

        carouselliveView = caroueltemplate.render(sideBarStreamList = streamQuery)  
        liveNowView      = liveNowtemplate.render(sideBarStreamList = streamQuery, sysSettingsprotected = sysSettings.protectionEnabled)  
    else:
        carouselliveView = ""
        liveNowView = ""

    emit('getViewerStuffResponse', {'data': str(carouselliveView),'sideBarStreamList': str(streamliveView),'liveNowList': str(liveNowView)})

    return 'OK'


@socketio.on('getViewerTotal')
def handle_viewer_total_request(streamData, room=None):
    channelLoc = str(streamData['data'])
    
    viewers = xmpp.getChannelCounts(channelLoc)

    # Why were we doing the below in a "getViewerTotal" function when this data is already provided?  Also "channelViewers"???

    #ChannelUpdateStatement = (update(Channel.Channel).where(Channel.Channel.channelLoc == channelLoc).values(channelViewers=viewers))
    #channelQuery = Channel.Channel.query.filter_by(channelLoc=channelLoc).with_entities(Channel.Channel.id).first()

    #StreamUpdateStatement = (update(Stream.Stream).where(Stream.Stream.linkedChannel == chanID).values(currentViewers=viewers))

    #db.session.commit()
    #db.session.close()
    if room is None:
        emit('viewerTotalResponse', {'data': str(viewers)})
    else:
        emit('viewerTotalResponse', {'data': str(viewers)}, room=room)
    return 'OK'

@socketio.on('updateStreamData')
def updateStreamData(message):
    channelLoc = message['channel']

    #sysSettings = settings.settings.query.first()
    sysSettings = settings.getSettingsFromRedis()

    channelQuery = Channel.Channel.query.filter_by(channelLoc=channelLoc, owningUser=current_user.id).first()

    if channelQuery is not None:
        stream = channelQuery.stream[0]
        stream.streamName = system.strip_html(message['name'])
        stream.topic = int(message['topic'])
        db.session.commit()

        if channelQuery.imageLocation is None:
            channelImage = (sysSettings.siteProtocol + sysSettings.siteAddress + "/static/img/video-placeholder.jpg")
        else:
            channelImage = (sysSettings.siteProtocol + sysSettings.siteAddress + "/images/" + channelQuery.imageLocation)

        webhookFunc.runWebhook(channelQuery.id, 4, channelname=channelQuery.channelName,
                   channelurl=(sysSettings.siteProtocol + sysSettings.siteAddress + "/channel/" + str(channelQuery.id)),
                   channeltopic=channelQuery.topic,
                   channelimage=channelImage, streamer=templateFilters.get_userName(channelQuery.owningUser),
                   channeldescription=str(channelQuery.description),
                   streamname=stream.streamName,
                   streamurl=(sysSettings.siteProtocol + sysSettings.siteAddress + "/view/" + channelQuery.channelLoc),
                   streamtopic=templateFilters.get_topicName(stream.topic),
                   streamimage=(sysSettings.siteProtocol + sysSettings.siteAddress + "/stream-thumb/" + channelQuery.channelLoc + ".png"))
        db.session.commit()
        db.session.close()
    db.session.commit()
    db.session.close()
    return 'OK'