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
from functions import templateFilters
from classes.settings import r

import jinja2 

streamers_bp = Blueprint('streamers', __name__, url_prefix='/streamer')

@streamers_bp.route('/')
def streamers_page():
    renderedstreamers = r.get('renderedstreamers')

    # if there is nothing in redis we need to get it and set it for everyone else
    if (renderedstreamers == None):

        sysSettings = settings.getSettingsFromRedis()
        streamerIDs = []

        if sysSettings.showEmptyTables:
            for channel in db.session.query(Channel.Channel.owningUser).distinct():
                if channel.owningUser not in streamerIDs:
                    streamerIDs.append(channel.owningUser)
        else:
            openStreams = Stream.Stream.query.all()
            for stream in openStreams:
                if stream.channel.owningUser not in streamerIDs:
                    streamerIDs.append(stream.channel.owningUser)
            for recordedVidInstance in db.session.query(RecordedVideo.RecordedVideo.owningUser).distinct():
                if recordedVidInstance.owningUser not in streamerIDs:
                    streamerIDs.append(recordedVidInstance.owningUser)

        streamerList = []
        for userID in streamerIDs:
            userQuery = Sec.User.query.filter_by(id=userID).first()
            if userQuery is not None:
                streamerList.append(userQuery)

        mtemplateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=mtemplateLoader)
        templateFilters.init(templateEnv)     
        streamerstemplate = templateEnv.get_template(themes.checkOverrideDirect('redisstreamers.html',sysSettings.systemTheme))

        renderedstreamers = streamerstemplate.render(streamerList=streamerList)  

        #print("rendered")
        r.set('renderedstreamers',renderedstreamers)
        r.expire('renderedstreamers', 60)  # timeout for redis 


    streamerList = [] # it's already set by render above

    return render_template(themes.checkOverride('streamers.html'), streamerList=streamerList, renderedstreamers = renderedstreamers)

@streamers_bp.route('/<userID>/')
def streamers_view_page(userID):
    userID = int(userID)

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

            return render_template(themes.checkOverride('videoListView.html'), openStreams=streams, recordedVids=recordedVideoQuery, userChannels=userChannels, clipsList=clipsList, title=streamerQuery.username, streamerData=streamerQuery)
    flash('Invalid Streamer','error')
    return redirect(url_for("root.main_page"))