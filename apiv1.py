import sys
from os import path, remove
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from flask import Blueprint, request, url_for
from flask_restplus import Api, Resource, reqparse
from flask_socketio import emit

import shutil
import uuid

from classes import Channel
from classes import Stream
from classes import RecordedVideo
from classes import topics
from classes import upvotes
from classes import apikey
from classes import views
from classes import settings
#from classes import hubConnection
from classes.shared import db
from classes.shared import socketio

class fixedAPI(Api):
    # Monkeyfixed API IAW https://github.com/noirbizarre/flask-restplus/issues/223
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api_v1 = Blueprint('api', __name__, url_prefix='/apiv1')
api = fixedAPI(api_v1, version='1.0', title='OSP API', description='OSP API for Users, Streamers, and Admins', default='Primary', default_label='OSP Primary Endpoints', authorizations=authorizations)

### Start API Functions ###

channelParserPut = reqparse.RequestParser()
channelParserPut.add_argument('channelName', type=str)
channelParserPut.add_argument('description', type=str)
channelParserPut.add_argument('topicID', type=int)

channelParserPost = reqparse.RequestParser()
channelParserPost.add_argument('channelName', type=str, required=True)
channelParserPost.add_argument('description', type=str, required=True)
channelParserPost.add_argument('topicID', type=int, required=True)
channelParserPost.add_argument('recordEnabled', type=bool, required=True)
channelParserPost.add_argument('chatEnabled', type=bool, required=True)

streamParserPut = reqparse.RequestParser()
streamParserPut.add_argument('streamName', type=str)
streamParserPut.add_argument('topicID', type=int)

videoParserPut = reqparse.RequestParser()
videoParserPut.add_argument('videoName', type=str)
videoParserPut.add_argument('description', type=str)
videoParserPut.add_argument('topicID', type=int)

clipParserPut = reqparse.RequestParser()
clipParserPut.add_argument('clipName', type=str)
clipParserPut.add_argument('description', type=str)
# TODO Add Clip Post Arguments

chatParserPost = reqparse.RequestParser()
chatParserPost.add_argument('username', type=str, required=True)
chatParserPost.add_argument('message', type=str, required=True)
chatParserPost.add_argument('userImage', type=str)

hubConnectionPost = reqparse.RequestParser()
hubConnectionPost.add_argument('verificationToken', type=str, required=True)
hubConnectionPost.add_argument('serverToken', type=str, required=True)

@api.route('/server')
class api_1_Server(Resource):
    # Server - Get Basic Server Information
    def get(self):
        """
            Displays a Listing of Server Settings
        """
        serverSettings = settings.settings.query.all()[0]
        db.session.commit()
        return {'results': serverSettings.serialize() }

@api.route('/channels/')
class api_1_ListChannels(Resource):
    # Channel - Get all Channels
    def get(self):
        """
            Gets a List of all Public Channels
        """
        channelList = Channel.Channel.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in channelList]}
    # Channel - Create Channel
    @api.expect(channelParserPost)
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def post(self):
        """
            Creates a New Channel
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    args = channelParserPost.parse_args()
                    newChannel = Channel.Channel(int(requestAPIKey.userID), str(uuid.uuid4()), args['channelName'], int(args['topicID']), args['recordEnabled'], args['chatEnabled'],args['description'])
                    db.session.add(newChannel)
                    db.session.commit()

                    return {'results': {'message':'Channel Created', 'apiKey':newChannel.streamKey}}, 200
        return {'results': {'message':"Request Error"}}, 400

@api.route('/channels/<string:channelEndpointID>')
@api.doc(params={'channelEndpointID': 'Channel Endpoint Descriptor, Expressed in a UUID Value(ex:db0fe456-7823-40e2-b40e-31147882138e)'})
class api_1_ListChannel(Resource):
    def get(self, channelEndpointID):
        """
            Get Info for One Channel
        """
        channelList = Channel.Channel.query.filter_by(channelLoc=channelEndpointID).all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in channelList]}
    # Channel - Change Channel Name or Topic ID
    @api.expect(channelParserPut)
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def put(self, channelEndpointID):
        """
            Change a Channel's Name or Topic
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(channelLoc=channelEndpointID, owningUser=requestAPIKey.userID).first()
                    if channelQuery != None:
                        args = channelParserPut.parse_args()
                        if 'channelName' in args:
                            if args['channelName'] is not None:
                                channelQuery.channelName = args['channelName']
                        if 'description' in args:
                            if args['description'] is not None:
                                channelQuery.description = args['channelName']
                        if 'topicID' in args:
                            if args['topicID'] is not None:
                                possibleTopics = topics.topics.query.filter_by(id=int(args['topicID'])).first()
                                if possibleTopics != None:
                                    channelQuery.topic = int(args['topicID'])
                        db.session.commit()
                        return {'results': {'message':'Channel Updated'}}, 200
        return {'results': {'message':'Request Error'}},400

    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def delete(self,channelEndpointID):
        """
            Deletes a Channel
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(channelLoc=channelEndpointID, owningUser=requestAPIKey.userID).first()
                    if channelQuery != None:
                        filePath = '/var/www/videos/' + channelQuery.channelLoc
                        if filePath != '/var/www/videos/':
                            shutil.rmtree(filePath, ignore_errors=True)

                        channelVid = channelQuery.recordedVideo
                        channelUpvotes = channelQuery.upvotes
                        channelStreams = channelQuery.stream

                        for entry in channelVid:
                            for upvote in entry.upvotes:
                                db.session.delete(upvote)
                            vidComments = entry.comments
                            for comment in vidComments:
                                db.session.delete(comment)
                            vidViews = views.views.query.filter_by(viewType=1, itemID=entry.id)
                            for view in vidViews:
                                db.session.delete(view)
                            db.session.delete(entry)
                        for entry in channelUpvotes:
                            db.session.delete(entry)
                        for entry in channelStreams:
                            db.session.delete(entry)
                        db.session.delete(channelQuery)
                        db.session.commit()
                        return {'results': {'message': 'Channel Deleted'}}, 200
        return {'results': {'message': 'Request Error'}}, 400

@api.route('/channels/chat/<string:channelEndpointID>')
@api.doc(params={'channelEndpointID': 'Channel Endpoint Descriptor, Expressed in a UUID Value(ex:db0fe456-7823-40e2-b40e-31147882138e)'})
class api_1_ChannelChat(Resource):
    @api.expect(chatParserPost)
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def post(self, channelEndpointID):
        """
            Creates a New Chat Message in the Channel
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(channelLoc=channelEndpointID, owningUser=requestAPIKey.userID).first()
                    if channelQuery != None:
                        args = chatParserPost.parse_args()
                        userImage = '/static/img/user2.png'
                        if 'userImage' in args:
                            if args['userImage'] is not None:
                                userImage = args['userImage']
                    socketio.emit('message', {'user': args['username'], 'image': userImage, 'msg': args['message'], 'flags': 'Bot'}, room=channelEndpointID)
                    return {'results': {'message': 'Message Posted'}}, 200
        return {'results': {'message': 'Request Error'}}, 400
@api.route('/streams/')
class api_1_ListStreams(Resource):
    def get(self):
        """
             Returns a List of All Active Streams
        """
        streamList = Stream.Stream.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in streamList]}

@api.route('/streams/<int:streamID>')
@api.doc(params={'streamID': 'ID Number for the Stream'})
class api_1_ListStream(Resource):
    def get(self, streamID):
        """
             Returns Info on a Single Active Streams
        """
        streamList = Stream.Stream.query.filter_by(id=streamID).all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in streamList]}
        # Channel - Change Channel Name or Topic ID

    @api.expect(channelParserPut)
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def put(self, streamID):
        """
            Change a Streams's Name or Topic
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    streamQuery = Stream.Stream.query.filter_by(id=int(streamID)).first()
                    if streamQuery != None:
                        if streamQuery.channel.owningUser == requestAPIKey.userID:
                            args = streamParserPut.parse_args()
                            if 'streamName' in args:
                                if args['streamName'] is not None:
                                    streamQuery.streamName = args['streamName']
                            if 'topicID' in args:
                                if args['topicID'] is not None:
                                    possibleTopics = topics.topics.query.filter_by(id=int(args['topicID'])).first()
                                    if possibleTopics != None:
                                        streamQuery.topic = int(args['topicID'])
                            db.session.commit()
                            return {'results': {'message': 'Stream Updated'}}, 200
        return {'results': {'message': 'Request Error'}}, 400

@api.route('/vids/')
class api_1_ListVideos(Resource):
    def get(self):
        """
             Returns a List of All Recorded Videos
        """
        videoList = RecordedVideo.RecordedVideo.query.filter_by(pending=False).all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in videoList]}

@api.route('/vids/<int:videoID>')
@api.doc(params={'videoID': 'ID Number for the Video'})
class api_1_ListVideo(Resource):
    def get(self, videoID):
        """
             Returns Info on a Single Recorded Video
        """
        videoList = RecordedVideo.RecordedVideo.query.filter_by(id=videoID).all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in videoList]}
    @api.expect(videoParserPut)
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def put(self, videoID):
        """
            Change a Video's Name, Description, or Topic
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    videoQuery = RecordedVideo.RecordedVideo.query.filter_by(id=int(videoID)).first()
                    if videoQuery != None:
                        if videoQuery.owningUser == requestAPIKey.userID:
                            args = videoParserPut.parse_args()
                            if 'videoName' in args:
                                if args['videoName'] is not None:
                                    videoQuery.channelName = args['videoName']
                            if 'topicID' in args:
                                if args['topicID'] is not None:
                                    possibleTopics = topics.topics.query.filter_by(id=int(args['topicID'])).first()
                                    if possibleTopics != None:
                                        videoQuery.topic = int(args['topicID'])
                            if 'description' in args:
                                if args['description'] is not None:
                                    videoQuery.description = args['description']
                            db.session.commit()
                            return {'results': {'message': 'Video Updated'}}, 200
        return {'results': {'message': 'Request Error'}}, 400
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def delete(self,videoID):
        """
            Deletes a Video
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    videoQuery = RecordedVideo.RecordedVideo.query.filter_by(id=videoID).first()
                    if videoQuery != None:
                        if videoQuery.owningUser == requestAPIKey.userID:
                            filePath = '/var/www/videos/' + videoQuery.videoLocation
                            thumbnailPath = '/var/www/videos/' + videoQuery.videoLocation[:-4] + ".png"

                            if filePath != '/var/www/videos/':
                                if path.exists(filePath) and (
                                        videoQuery.videoLocation != None or videoQuery.videoLocation != ""):
                                    remove(filePath)
                                    if path.exists(thumbnailPath):
                                        remove(thumbnailPath)
                            upvoteQuery = upvotes.videoUpvotes.query.filter_by(videoID=videoQuery.id).all()
                            for vote in upvoteQuery:
                                db.session.delete(vote)
                            vidComments = videoQuery.comments
                            for comment in vidComments:
                                db.session.delete(comment)
                            vidViews = views.views.query.filter_by(viewType=1, itemID=videoQuery.id)
                            for view in vidViews:
                                db.session.delete(view)
                            db.session.delete(videoQuery)
                            db.session.commit()
                            return {'results': {'message': 'Video Deleted'}}, 200
        return {'results': {'message': 'Request Error'}}, 400

@api.route('/clips/')
class api_1_ListClips(Resource):
    def get(self):
        """
             Returns a List of All Saved Clips
        """
        clipsList = RecordedVideo.Clips.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in clipsList]}

@api.route('/clips/<int:clipID>')
@api.doc(params={'clipID': 'ID Number for the Clip'})
class api_1_ListClip(Resource):
    def get(self, clipID):
        """
             Returns Info on a Single Saved Clip
        """
        clipList = RecordedVideo.Clips.query.filter_by(id=clipID).all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in clipList]}

    @api.expect(clipParserPut)
    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def put(self, clipID):
        """
            Change a Clip's Name or Description
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    clipQuery = RecordedVideo.Clips.query.filter_by(id=int(clipID)).first()
                    if clipQuery != None:
                        if clipQuery.recordedVideo.owningUser == requestAPIKey.userID:
                            args = clipParserPut.parse_args()
                            if 'clipName' in args:
                                if args['clipName'] is not None:
                                    clipQuery.clipName = args['clipName']
                            if 'description' in args:
                                if args['description'] is not None:
                                    clipQuery.description = args['description']
                            db.session.commit()
                            return {'results': {'message': 'Clip Updated'}}, 200
        return {'results': {'message': 'Request Error'}}, 400

    @api.doc(security='apikey')
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def delete(self, clipID):
        """
            Deletes a Clip
        """
        if 'X-API-KEY' in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers['X-API-KEY']).first()
            if requestAPIKey != None:
                if requestAPIKey.isValid():
                    clipQuery = RecordedVideo.Clips.query.filter_by(id=clipID).first()
                    if clipQuery != None:
                        if clipQuery.owningUser == requestAPIKey.userID:
                            thumbnailPath = '/var/www/videos/' + clipQuery.thumbnailLocation

                            if thumbnailPath != '/var/www/videos/':
                                if path.exists(thumbnailPath) and clipQuery.thumbnailLocation != None and clipQuery.thumbnailLocation != "":
                                    remove(thumbnailPath)
                            upvoteQuery = upvotes.clipUpvotes.query.filter_by(clipID=clipQuery.id).all()
                            for vote in upvoteQuery:
                                db.session.delete(vote)

                            db.session.delete(clipQuery)
                            db.session.commit()
                            return {'results': {'message': 'Clip Deleted'}}, 200
        return {'results': {'message': 'Request Error'}}, 400


@api.route('/topics/')
class api_1_ListTopics(Resource):
    def get(self):
        """
             Returns a List of All Topics
        """
        topicList = topics.topics.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in topicList]}

@api.route('/topics/<int:topicID>')
@api.doc(params={'topicID': 'ID Number for Topic'})
class api_1_ListTopic(Resource):
    def get(self, topicID):
        """
             Returns Info on a Single Topic
        """
        topicList = topics.topics.query.filter_by(id=topicID).all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in topicList]}

#@api.route('/hub/validateServer')
#class api_1_hubValidateServer(Resource):
#    """
#        Endpoint for an OSP Hub Server to Validate the Connection to a Node
#    """
#    @api.expect(hubConnectionPost)
#    def post(self):
#        args = hubConnectionPost.parse_args()
#        if 'verificationToken' in args:
#            connectionQuery = hubConnection.hubConnection.query.filter_by(verificationToken=args['verificationToken']).first()
#               if 'serverToken' in args:
#                    connectionQuery.validateHub(args['serverToken'])
#                    db.session.commit()
#                    return {'results': {'message': 'Server Validated with OSP Hub'}}, 200
#        return {'results': {'message': 'Request Error'}}, 400