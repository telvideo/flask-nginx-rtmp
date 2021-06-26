from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_security import current_user

from classes import settings
from classes import Channel
from classes import RecordedVideo
from classes import Stream
from classes import subscriptions
from classes import Sec

from functions import themes

channels_bp = Blueprint('channel', __name__, url_prefix='/channel')

@channels_bp.route('/')
def channels_page():
    #sysSettings = settings.settings.query.first()
    sysSettings = settings.getSettingsFromRedis()
    
#    if sysSettings.showEmptyTables:
#        chanQuery = Channel.Channel.query.all()
#    else:
    chanQuery = Channel.Channel.query.join(Sec.User,Sec.User.id == Channel.Channel.owningUser).with_entities(Channel.Channel.topic,
            Channel.Channel.protected,
            Channel.Channel.Nsubscriptions,
            Channel.Channel.views,
            Channel.Channel.channelName,
            Channel.Channel.imageLocation,
            Channel.Channel.owningUser,
            Sec.User.username,
            Sec.User.pictureLocation,
            Channel.Channel.id).order_by(Channel.Channel.channelName.desc()).all()
      

    streamSet = set()
    streamQuery = Stream.Stream.query.with_entities(Stream.Stream.linkedChannel).all()
    for aStream in streamQuery:
        streamSet.add(aStream.linkedChannel) 

    channelList = []

    for chan in chanQuery:
        if chan.id in streamSet:
            isStreaming = True
        else:
            isStreaming = False
            
        aChan = {"protected":chan.protected,
        "id":chan.id,
        "owningUser":chan.owningUser,
        "Nsubscriptions":chan.Nsubscriptions,
        "views":chan.views,
        "imageLocation":chan.imageLocation,
        "channelName":chan.channelName,
        "topic":chan.topic,
        "username":chan.username,
        "isStreaming":isStreaming,
        "pictureLocation":chan.pictureLocation}
#            "totalViewers":achan.totalViewers,
#            "username": achan.username,
#            "channelName":achan.channelName,
#            "verified":achan.verified}
        channelList.append(aChan) 


    return render_template(themes.checkOverride('channels.html'), channelList=channelList)

@channels_bp.route('/<int:chanID>/')
def channel_view_page(chanID):
    chanID = int(chanID)
    channelData = Channel.Channel.query.filter_by(id=chanID).first()

    if channelData is not None:

        openStreams = Stream.Stream.query.filter_by(linkedChannel=chanID).all()
        recordedVids = RecordedVideo.RecordedVideo.query.filter_by(channelID=chanID, pending=False, published=True).order_by(
            RecordedVideo.RecordedVideo. videoDate.desc()).all()

       
        clipsList = []
        for vid in recordedVids:
            for clip in vid.clips:
                if clip.published is True:
                    clipsList.append(clip)

        clipsList.sort(key=lambda x: x.views, reverse=True)

        subState = False
        if current_user.is_authenticated:
            chanSubQuery = subscriptions.channelSubs.query.filter_by(channelID=channelData.id, userID=current_user.id).first()
            if chanSubQuery is not None:
                subState = True

        return render_template(themes.checkOverride('videoListView.html'), channelData=channelData, openStreams=openStreams, recordedVids=recordedVids, clipsList=clipsList, subState=subState, title="Channels - Videos")
    else:
        flash("No Such Channel", "error")
        return redirect(url_for("root.main_page"))

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