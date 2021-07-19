from flask_socketio import emit
from flask_security import current_user
from sqlalchemy import update
from flask import render_template
from classes.shared import db, socketio
from classes import Channel
from classes import Stream
from classes import settings
from classes import Sec

from functions import system
from functions import webhookFunc
from functions import templateFilters
from functions import xmpp
from functions import themes

from app import r

import jinja2
    
mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
mtemplateEnv = jinja2.Environment(loader=mtemplateLoader)
mTEMPLATE_FILE = "/templates/liveStreams.html"
mtemplate = mtemplateEnv.get_template(mTEMPLATE_FILE)

@socketio.on('getViewerStuff')
def handle_viewer_Stuff():

    # chanSubQuery = subscriptions.channelSubs.query.filter_by(userID=current_user.id).all()
    chanSubQuery = []

 #   if current_user.is_authenticated:
 #       chanSubQuery = subscriptions.channelSubs.query.filter_by(userID=current_user.id).\
 #           join(Channel.Channel, Channel.Channel.id == subscriptions.channelSubs.channelID ).\
 #           with_entities(Channel.Channel.imageLocation,Channel.Channel.id,Channel.Channel.channelName)

    
    #  streamQuery = Stream.Stream.query.order_by(Stream.Stream.currentViewers).all()
    streamQuery = Stream.Stream.query.join(Channel.Channel, Channel.Channel.id == Stream.Stream.linkedChannel) \
    .join(Sec.User, Sec.User.id == Channel.Channel.owningUser).with_entities(Stream.Stream.id,
#        Stream.Stream.uuid,
#        Stream.Stream.startTimestamp,
        Stream.Stream.linkedChannel,
#        Stream.Stream.streamKey,
#        Stream.Stream.streamName,
#        Stream.Stream.topic,
        Stream.Stream.currentViewers,
        Stream.Stream.totalViewers,
#        Stream.Stream.rtmpServer,
        Stream.Stream.NupVotes,
        Channel.Channel.channelLoc,
#        Sec.User.pictureLocation,
#        Sec.User.verified,
#        Channel.Channel.imageLocation,
        Sec.User.username,
#        Channel.Channel.channelName
        ).order_by(Stream.Stream.currentViewers.desc()).all()
   
    
     #liveView = "FROM STREAM" #render_template(themes.checkOverride('liveStreams.html'))  
    #streamliveView = render_template(themes.checkOverride('liveStreams.html'),sideBarStreamList = streamQuery)  
    
    #streamliveView = render_template('liveStreams.html',sideBarStreamList = streamQuery)  


    streamliveView = mtemplate.render(sideBarStreamList = streamQuery)  
    

    carouselliveView = "TESTrender_templateTest"  
    
    emit('getViewerStuffResponse', {'data': str(carouselliveView),'sideBarStreamList': str(streamliveView)})

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