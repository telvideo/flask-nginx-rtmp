import sys
from os import path, remove
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from flask import Blueprint, request, url_for, render_template, redirect, flash

from classes.shared import db
from classes import settings
from classes import Channel
from classes import RecordedVideo
from classes import Stream
from classes import Sec

from functions import themes

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/<username>')
def profile_view_page(username):
    #userQuery = Sec.User.query.filter_by(username=username).first()
    userQuery = Sec.User.query.filter_by(username=username).with_entities(\
        Sec.User.id,
        Sec.User.pictureLocation,
        Sec.User.username,
        Sec.User.biography).first()
   
    if userQuery is  None:
        flash('Invalid User','error')
        return redirect(url_for("root.main_page"))

    userID = userQuery.id
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
        .join(Sec.User, Sec.User.id == Channel.Channel.owningUser)\
        .filter(Channel.Channel.owningUser == userID)\
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

    userChannels = []
    strSet = set()
    for stre in openStreams:
        strSet.add(stre.linkedChannel)

    for chan in chans:
        if chan.id in strSet:
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
            "description":chan.description,
            "topic":chan.topic
            }
       
        userChannels.append(channelData)

    recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(owningUser=userID, pending=False, published=True)\
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
             .filter(RecordedVideo.RecordedVideo.owningUser == userID, RecordedVideo.Clips.published == True ).with_entities(
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

    return render_template(themes.checkOverride('videoListView.html'), openStreams=openStreams, recordedVids=recordedVideoQuery, userChannels=userChannels, clipsList=clipsList, title=userQuery.username, streamerData=userQuery)
#
#    userQuery = Sec.User.query.filter_by(username=username).first()
#    if userQuery is not None:
#        userChannels = Channel.Channel.query.filter_by(owningUser=userQuery.id).all()#
#
#        streams = []
#
#        for channel in userChannels:
#            for stream in channel.stream:
#                streams.append(stream)
#
#        recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(owningUser=userQuery.id, pending=False, published=True).all()
#
#        # Sort Video to Show Newest First
#        recordedVideoQuery.sort(key=lambda x: x.videoDate, reverse=True)
#
#        clipsList = []
#        for vid in recordedVideoQuery:
#            for clip in vid.clips:
#                if clip.published is True:
#                    clipsList.append(clip)
#
#        clipsList.sort(key=lambda x: x.views, reverse=True)
#
#        return render_template(themes.checkOverride('videoListView.html'), openStreams=streams, recordedVids=recordedVideoQuery, userChannels=userChannels, clipsList=clipsList, title=userQuery.username, streamerData=userQuery)
#    flash('Invalid User','error')
#    return redirect(url_for("root.main_page"))