from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_security import current_user

from classes import settings
from classes import Channel
from classes import RecordedVideo
from classes import Stream
from classes import subscriptions
from classes import Sec
from classes import topics
from globals import globalvars
from functions import templateFilters

from functions import themes

channels_bp = Blueprint('channel', __name__, url_prefix='/channel')


from classes.settings import r

import jinja2  # we can't just use standard render_template() cos that will fire all our global injects and other stuff
    

@channels_bp.route('/')
def channels_page():

    renderedchannels = r.get('renderedchannels')

    # if there is nothing in redis we need to get it and set it for everyone else
    if (renderedchannels == None):
        sysSettings = settings.getSettingsFromRedis()
            
        if sysSettings.showEmptyTables:
            channelList = Channel.Channel.query.all()
        else:
            channelList = []
            for channel in Channel.Channel.query.all():
                if len(channel.recordedVideo) > 0:
                    channelList.append(channel)

        mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=mtemplateLoader)
        templateFilters.init(templateEnv)
     
        channelstemplate = templateEnv.get_template(themes.checkOverrideDirect('redischannels.html',sysSettings.systemTheme))

        renderedchannels = channelstemplate.render(channelList=channelList)  

        #print("rendered")
        r.set('renderedchannels',renderedchannels)
        r.expire('renderedchannels', 60)  # timeout for redis 

    channelList = []

    return render_template(themes.checkOverride('channels.html'), channeldList=channelList, renderedchannels = renderedchannels)


@channels_bp.route('/<int:chanID>/')
def channel_view_page(chanID):
    chanID = int(chanID)

    chan = Channel.Channel.query.join(Sec.User,Sec.User.id == Channel.Channel.owningUser).with_entities(
        Channel.Channel.protected,
        Channel.Channel.Nsubscriptions,
        Channel.Channel.views,
        Channel.Channel.channelName,
        Channel.Channel.imageLocation,
        Channel.Channel.owningUser,
        Channel.Channel.description,
        Channel.Channel.topic,
        Channel.Channel.id,
        Channel.Channel.channelLoc,
        Sec.User.username,
        Sec.User.pictureLocation).filter(Channel.Channel.id == chanID).first()

    if chan is None:
        flash("No Such Channel", "error")
        return redirect(url_for("root.main_page"))


    openStreams = Stream.Stream.query\
        .join(Channel.Channel,Channel.Channel.id == Stream.Stream.linkedChannel)\
        .join(Sec.User, Sec.User.id == Channel.Channel.owningUser)\
        .filter(Channel.Channel.id == chanID)\
            .with_entities(
            Channel.Channel.channelLoc,
            Channel.Channel.protected,
            Channel.Channel.id.label('chanID'),
            Channel.Channel.channelName,
            Stream.Stream.streamName,
            Stream.Stream.topic,
            Stream.Stream.NupVotes,
            Stream.Stream.currentViewers,
            Stream.Stream.totalViewers,
            Stream.Stream.linkedChannel,
            Sec.User.pictureLocation
            ).all()
 
    if openStreams:
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
        "channelLoc":chan.channelLoc,
        "username":chan.username,
        "isStreaming":isStreaming,
        "pictureLocation":chan.pictureLocation,
        "description":chan.description,
        "topic":chan.topic
        }
    
    recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(channelID=chanID, pending=False, published=True)\
        .join(Sec.User,Sec.User.id == RecordedVideo.RecordedVideo.owningUser)\
        .join(Channel.Channel,Channel.Channel.id == RecordedVideo.RecordedVideo.channelID)\
        .with_entities(
        Channel.Channel.protected,
        Channel.Channel.id.label('chanID'),
        Channel.Channel.channelName.label('chanchannelName'),
        RecordedVideo.RecordedVideo.channelName,
        RecordedVideo.RecordedVideo.id,
        RecordedVideo.RecordedVideo.gifLocation,
        RecordedVideo.RecordedVideo.thumbnailLocation,
        RecordedVideo.RecordedVideo.videoDate,
        RecordedVideo.RecordedVideo.topic,
        RecordedVideo.RecordedVideo.owningUser,
        RecordedVideo.RecordedVideo.length,
        RecordedVideo.RecordedVideo.views,
        RecordedVideo.RecordedVideo.NupVotes,
        Sec.User.username,
        Sec.User.pictureLocation
        ).all()
  
    clipsList = RecordedVideo.Clips.query\
        .join(RecordedVideo.RecordedVideo,RecordedVideo.RecordedVideo.id == RecordedVideo.Clips.parentVideo)\
        .join(Channel.Channel,Channel.Channel.id == RecordedVideo.RecordedVideo.owningUser)\
        .join(Sec.User,Sec.User.id == RecordedVideo.RecordedVideo.owningUser)\
        .filter(RecordedVideo.RecordedVideo.channelID == chanID, RecordedVideo.Clips.published == True ).with_entities(
        RecordedVideo.RecordedVideo.gifLocation,
        RecordedVideo.RecordedVideo.thumbnailLocation,
        RecordedVideo.RecordedVideo.videoDate,
        RecordedVideo.RecordedVideo.topic,
        RecordedVideo.RecordedVideo.owningUser,
        RecordedVideo.Clips.id,
        RecordedVideo.Clips.clipName,
        RecordedVideo.Clips.NupVotes,
        RecordedVideo.Clips.views,
        RecordedVideo.Clips.length,
        Channel.Channel.protected,
        Channel.Channel.id.label('chanID'),
        Channel.Channel.channelName,
        Sec.User.username,
        Sec.User.pictureLocation
        ).all()


    subState = False
    if current_user.is_authenticated:
        chanSubQuery = subscriptions.channelSubs.query.filter_by(channelID=chanID, userID=current_user.id).first()
        if chanSubQuery is not None:
            subState = True

    return render_template(themes.checkOverride('videoListView.html'), channelData=channelData, openStreams=openStreams, recordedVids=recordedVideoQuery, clipsList=clipsList, subState=subState, title="Channels - Videos")

#
#    channelData = Channel.Channel.query.filter_by(id=chanID).first()
#    if channelData is not None:

#        openStreams = Stream.Stream.query.filter_by(linkedChannel=chanID).all()
#        recordedVids = RecordedVideo.RecordedVideo.query.filter_by(channelID=chanID, pending=False, published=True).order_by(
#            RecordedVideo.RecordedVideo. videoDate.desc()).all()
       
#        clipsList = []
#        for vid in recordedVids:
#            for clip in vid.clips:
#                if clip.published is True:
#                    clipsList.append(clip)

#        clipsList.sort(key=lambda x: x.views, reverse=True)

#        subState = False
#        if current_user.is_authenticated:
#            chanSubQuery = subscriptions.channelSubs.query.filter_by(channelID=channelData.id, userID=current_user.id).first()
#            if chanSubQuery is not None:
#                subState = True
#
#        return render_template(themes.checkOverride('videoListView.html'), channelData=channelData, openStreams=openStreams, recordedVids=recordedVids, clipsList=clipsList, subState=subState, title="Channels - Videos")
#    else:
#        flash("No Such Channel", "error")
#        return redirect(url_for("root.main_page"))

@channels_bp.route('/link/<channelLoc>/')
def channel_view_link_page(channelLoc):
    if channelLoc is not None:
        channelQuery = Channel.Channel.query.filter_by(channelLoc=str(channelLoc)).first()
        if channelQuery is not None:
            return redirect(url_for(".channel_view_page",chanID=channelQuery.id))
    flash("Invalid Channel Location", "error")
    return redirect(url_for("root.main_page"))

# Allow a direct link to any open stream for a channel
@channels_bp.route('/<loc>/stream')
def channel_stream_link_page(loc):
    requestedChannel = Channel.Channel.query.filter_by(id=int(loc)).first()
    if requestedChannel is not None:
        openStreamQuery = Stream.Stream.query.filter_by(linkedChannel=requestedChannel.id).first()
        if openStreamQuery is not None:
            return redirect(url_for("view_page", loc=requestedChannel.channelLoc))
        else:
            flash("No Active Streams for the Channel","error")
            return redirect(url_for(".channel_view_page",chanID=requestedChannel.id))
    else:
        flash("Unknown Channel","error")
        return redirect(url_for("root.main_page"))