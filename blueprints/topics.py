from flask import Blueprint, request, url_for, render_template, redirect, flash

from classes.shared import db
from classes import settings
from classes import topics
from classes import Stream
from classes import Channel
from classes import RecordedVideo
from classes import Sec
from functions import templateFilters
from functions import themes
from classes.settings import r

import jinja2  

topics_bp = Blueprint('topic', __name__, url_prefix='/topic')

@topics_bp.route('/')
def topic_page():

    renderedtopics = r.get('renderedtopics')
    topicsList = []

    # if there is nothing in redis we need to get it and set it for everyone else
    if (renderedtopics == None):
  
        sysSettings = settings.getSettingsFromRedis()
        if sysSettings.showEmptyTables:
            topicsList = topics.topics.query.all() 
        else:
            topicIDList = []
            for streamInstance in db.session.query(Stream.Stream.topic).distinct():
                topicIDList.append(streamInstance.topic)
            for recordedVidInstance in db.session.query(RecordedVideo.RecordedVideo.topic).distinct():
                if recordedVidInstance.topic not in topicIDList:
                    topicIDList.append(recordedVidInstance.topic)

            for item in topicIDList:
                topicQuery = topics.topics.query.filter_by(id=item).first()
                if topicQuery is not None:
                    topicsList.append(topicQuery)

        topicsList.sort(key=lambda x: x.name.lower())


        mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=mtemplateLoader)
        templateFilters.init(templateEnv)     
        topicstemplate = templateEnv.get_template(themes.checkOverrideDirect('redistopics.html',sysSettings.systemTheme))

        renderedtopics = topicstemplate.render(topicsList=topicsList)  

        #print("rendered")
        r.set('renderedtopics',renderedtopics)
        r.expire('renderedtopics', 60)  # timeout for redis 

    return render_template(themes.checkOverride('topics.html'), topicsList=topicsList, renderedtopics = renderedtopics)


@topics_bp.route('/<topicID>/')
def topic_view_page(topicID):
    topicID = int(topicID)

    streamsQuery = Stream.Stream.query\
        .join(Channel.Channel,Channel.Channel.id == Stream.Stream.linkedChannel)\
        .join(Sec.User, Sec.User.id == Channel.Channel.owningUser)\
        .filter(Channel.Channel.topic == topicID)\
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

    recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(topic=topicID, pending=False, published=True)\
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
        .filter(RecordedVideo.RecordedVideo.topic == topicID, RecordedVideo.Clips.published == True ).with_entities(
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

    return render_template(themes.checkOverride('videoListView.html'), openStreams=streamsQuery, recordedVids=recordedVideoQuery, clipsList=clipsList, title="Topics - Videos")

#    streamsQuery = Stream.Stream.query.filter_by(topic=topicID).all()
#    recordedVideoQuery = RecordedVideo.RecordedVideo.query.filter_by(topic=topicID, pending=False, published=True).all()
#
#    # Sort Video to Show Newest First
#    recordedVideoQuery.sort(key=lambda x: x.videoDate, reverse=True)
#
#    clipsList = []
#    for vid in recordedVideoQuery:
#        for clip in vid.clips:
#            if clip.published is True:
#                clipsList.append(clip)
#
#    clipsList.sort(key=lambda x: x.views, reverse=True)
#
#    return render_template(themes.checkOverride('videoListView.html'), openStreams=streamsQuery, recordedVids=recordedVideoQuery, clipsList=clipsList, title="Topics - Videos")
