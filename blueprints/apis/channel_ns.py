from flask_restx import Api, Resource, reqparse, Namespace
from flask import request

import uuid
import shutil
import socket

from classes import settings
from classes import Channel
from classes import apikey
from classes import Sec
from classes import topics
from classes import invites
from classes import views
from classes import Stream
from classes.shared import db

from functions import system
from functions import cachedDbCalls
from functions import channelFunc
from functions import templateFilters
from functions import apiFunc


from globals import globalvars

api = Namespace("channel", description="Channels Related Queries and Functions")

channelRestreamPOST = reqparse.RequestParser()
channelRestreamPOST.add_argument('name', type=str, required=True)
channelRestreamPOST.add_argument('url', type=str, required=True)
channelRestreamPOST.add_argument('enabled', type=str)

channelGetParser = reqparse.RequestParser()
channelGetParser.add_argument('userID', type=int, required=False, help='The unique identifier of the user. **Admin API is required**')


channelRestreamPUT = reqparse.RequestParser()
channelRestreamPUT.add_argument('id', type=str, required=True)
channelRestreamPUT.add_argument('name', type=str, required=True)
channelRestreamPUT.add_argument('url', type=str, required=True)
channelRestreamPUT.add_argument('enabled', type=str)



channelParserPut = reqparse.RequestParser()
channelParserPut.add_argument("channelName", type=str)
channelParserPut.add_argument("description", type=str)
channelParserPut.add_argument("topicID", type=int)

channelParserPost = reqparse.RequestParser()
channelParserPost.add_argument("channelName", type=str, required=True)
channelParserPost.add_argument("description", type=str, required=True)
channelParserPost.add_argument("topicID", type=int, required=True)
channelParserPost.add_argument("recordEnabled", type=bool, required=True)
channelParserPost.add_argument("chatEnabled", type=bool, required=True)
channelParserPost.add_argument("showHome", type=bool, required=True)
channelParserPost.add_argument("commentsEnabled", type=bool, required=True)

channelInviteGetInvite = reqparse.RequestParser()
channelInviteGetInvite.add_argument("userID", type=int)

channelInvitePostInvite = reqparse.RequestParser()
channelInvitePostInvite.add_argument("userID", type=int, required=True)
channelInvitePostInvite.add_argument("expirationDays", type=int, required=True)

channelInviteDeleteInvite = reqparse.RequestParser()
channelInviteDeleteInvite.add_argument("userID", type=int, required=True)

channelSearchPost = reqparse.RequestParser()
channelSearchPost.add_argument("term", type=str, required=True)


def checkRTMPAuthIP(requestData):
    authorized = False
    requestIP = "0.0.0.0"
    if requestData.environ.get("HTTP_X_FORWARDED_FOR") is None:
        requestIP = requestData.environ["REMOTE_ADDR"]
    else:
        requestIP = requestData.environ["HTTP_X_FORWARDED_FOR"]

    authorizedRTMPServers = settings.rtmpServer.query.with_entities(
        settings.rtmpServer.id,
        settings.rtmpServer.hide,
        settings.rtmpServer.active,
        settings.rtmpServer.address,
    ).all()

    receivedIP = requestIP
    ipList = requestIP.split(",")
    confirmedIP = ""
    for ip in ipList:
        parsedip = ip.strip()
        for server in authorizedRTMPServers:
            if authorized is False:
                if server.active is True:
                    resolveResults = socket.getaddrinfo(server.address, 0)
                    for resolved in resolveResults:
                        if parsedip == resolved[4][0]:
                            authorized = True
                            confirmedIP = resolved[4][0]

    if authorized is False:
        confirmedIP = receivedIP
        system.newLog(1, "Unauthorized RTMP Server - " + confirmedIP)

    return (authorized, confirmedIP)


@api.route("/")
class api_1_ListChannels(Resource):
    # Channel - Get all Channels
    @api.expect(channelGetParser)
    def get(self):
        """
        Gets a List of all Public Channels or channels by a specific user if requested by an admin
        """
        args = channelGetParser.parse_args()
        user_id = args.get('userID')

        # When user ID is provided, check if the request is from an admin
        if user_id is not None:
            if "X-API-KEY" not in request.headers or not apiFunc.isValidAdminKey(request.headers["X-API-KEY"]):
                return {"results": {"message": "Unauthorized access. Admin only."}}, 403
            
            # Filter channels by user ID if admin
            channels = Channel.Channel.query.filter_by(owningUser=user_id).all()
            return {"results": cachedDbCalls.serializeChannels(channels)}

        # Return all channels if no user ID is provided
        return {"results": cachedDbCalls.serializeChannels()}


    # Channel - Create Channel
    @api.expect(channelParserPost)
    @api.doc(security="apikey")
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def post(self):
        """
        Creates a New Channel
        """
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    args = channelParserPost.parse_args()
                    newChannel = Channel.Channel(
                        int(requestAPIKey.userID),
                        str(uuid.uuid4()),
                        args["channelName"],
                        int(args["topicID"]),
                        args["recordEnabled"],
                        args["chatEnabled"],
                        args["commentsEnabled"],
                        args["showHome"],
                        args["description"],
                    )

                    userQuery = Sec.User.query.filter_by(
                        id=int(requestAPIKey.userID)
                    ).first()

                    # Establish XMPP Channel
                    from app import ejabberd

                    sysSettings = cachedDbCalls.getSystemSettings()
                    ejabberd.create_room(
                        newChannel.channelLoc,
                        "conference." + sysSettings.siteAddress,
                        sysSettings.siteAddress,
                    )
                    ejabberd.set_room_affiliation(
                        newChannel.channelLoc,
                        "conference." + sysSettings.siteAddress,
                        str(userQuery.uuid) + "@" + sysSettings.siteAddress,
                        "owner",
                    )

                    # Default values
                    for key, value in globalvars.room_config.items():
                        ejabberd.change_room_option(
                            newChannel.channelLoc,
                            "conference." + sysSettings.siteAddress,
                            key,
                            value,
                        )

                    # Name and title
                    ejabberd.change_room_option(
                        newChannel.channelLoc,
                        "conference." + sysSettings.siteAddress,
                        "title",
                        newChannel.channelName,
                    )
                    ejabberd.change_room_option(
                        newChannel.channelLoc,
                        "conference." + sysSettings.siteAddress,
                        "description",
                        userQuery.username
                        + 's chat room for the channel "'
                        + newChannel.channelName
                        + '"',
                    )

                    db.session.add(newChannel)
                    db.session.commit()

                    return {
                        "results": {
                            "message": "Channel Created",
                            "apiKey": newChannel.streamKey,
                        }
                    }, 200
        return {"results": {"message": "Request Error"}}, 400


@api.route("/<string:channelEndpointID>")
@api.doc(security="apikey")
@api.doc(
    params={
        "channelEndpointID": "Channel Endpoint Descriptor, Expressed in a UUID Value(ex:db0fe456-7823-40e2-b40e-31147882138e)"
    }
)
class api_1_ListChannel(Resource):
    def get(self, channelEndpointID):
        """
        Get Info for One Channel
        """
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(
                        channelLoc=channelEndpointID, owningUser=requestAPIKey.userID
                    ).all()
                    if channelQuery != []:
                        db.session.commit()
                        return {
                            "results": [ob.authed_serialize() for ob in channelQuery]
                        }
                return {"results": {"message": "Request Error"}}, 400
        else:
            return {
                "results": [
                    cachedDbCalls.serializeChannelByLocationID(channelEndpointID)
                ]
            }

    # Channel - Change Channel Name or Topic ID
    @api.expect(channelParserPut)
    @api.doc(security="apikey")
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def put(self, channelEndpointID):
        """
        Change a Channel's Name or Topic
        """
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(
                        channelLoc=channelEndpointID, owningUser=requestAPIKey.userID
                    ).first()
                    if channelQuery is not None:
                        args = channelParserPut.parse_args()
                        if "channelName" in args:
                            if args["channelName"] is not None:
                                channelQuery.channelName = args["channelName"]
                        if "description" in args:
                            if args["description"] is not None:
                                channelQuery.description = args["channelName"]
                        if "topicID" in args:
                            if args["topicID"] is not None:
                                possibleTopics = topics.topics.query.filter_by(
                                    id=int(args["topicID"])
                                ).first()
                                if possibleTopics is not None:
                                    channelQuery.topic = int(args["topicID"])

                        # Invalidate Channel Cache
                        cachedDbCalls.invalidateChannelCache(channelQuery.id)

                        db.session.commit()

                        return {"results": {"message": "Channel Updated"}}, 200
        return {"results": {"message": "Request Error"}}, 400

    @api.doc(security="apikey")
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def delete(self, channelEndpointID):
        """
        Deletes a Channel
        """
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(
                        channelLoc=channelEndpointID, owningUser=requestAPIKey.userID
                    ).first()
                    if channelQuery is not None:
                        results = channelFunc.delete_channel(channelQuery.id)

                        # Invalidate Channel Cache
                        cachedDbCalls.invalidateChannelCache(channelQuery.id)

                        db.session.commit()

                        return {"results": {"message": "Channel Deleted"}}, 200
        return {"results": {"message": "Request Error"}}, 400

@api.route("/activeChannels")
class api_1_ActiveChannels(Resource):
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def get(self):
        """
        Returns list of active channels
        """
        sysSettings = cachedDbCalls.getSystemSettings()
        activeChannels = cachedDbCalls.getLiveChannels()
        return  {"results": activeChannels }, 200

@api.route("/hubChannels")
class api_1_hubChannels(Resource):
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def get(self):
        """
        Returns list of Hub Enabled channels
        """
        sysSettings = cachedDbCalls.getSystemSettings()
        channels = cachedDbCalls.getHubChannels()
        return  {"results": channels }, 200

@api.route("/hubChannelsLive")
class api_1_ActiveHubChannels(Resource):
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def get(self):
        """
        Returns list of active channels
        """
        sysSettings = cachedDbCalls.getSystemSettings()
        activeChannels = cachedDbCalls.getLiveChannels(hubCheck=False)
        return  {"results": activeChannels }, 200

# Invites Endpoint for a Channel
@api.route("/<string:channelEndpointID>/streams")
@api.doc(params={"channelEndpointID": "GUID Channel Location"})
class api_1_Streams(Resource):
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def get(self, channelEndpointID):
        """
        Returns list of active streams on a channel
        """
        sysSettings = cachedDbCalls.getSystemSettings()
        channelIDQuery = cachedDbCalls.getChannelIDFromLocation(channelEndpointID)

        if channelIDQuery is not None:
            StreamQuery = cachedDbCalls.getChanneActiveStreams(channelIDQuery)

            results = []
            if sysSettings.adaptiveStreaming is True:
                streamURL = "/live-adapt/" + channelEndpointID + ".m3u8"
            else:
                streamURL = "/live/" + channelEndpointID + "/index.m3u8"
            for entry in StreamQuery:
                results.append(
                    {
                        "id": entry.id,
                        "uuid": entry.uuid,
                        "topic": entry.topic,
                        "streamName": entry.streamName,
                        "startTimestamp": str(entry.startTimestamp),
                        "currentViewers": entry.currentViewers,
                        "totalViewers": entry.totalViewers,
                        "streamURL": streamURL,
                    }
                )
            db.session.commit()
            return {"results": results}

        db.session.commit()
        return {"results": {"message": "Request Error"}}, 400


# TODO Add Ability to Add/Delete/Change
@api.route("/<string:channelEndpointID>/restreams")
@api.doc(security="apikey")
@api.doc(params={"channelEndpointID": "GUID Channel Location"})
class api_1_GetRestreams(Resource):
    def get(self, channelEndpointID):
        """
        Returns all restream destinations for a channel
        """

        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    channelData = (
                        Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID,
                            owningUser=requestAPIKey.userID,
                        )
                        .with_entities(Channel.Channel.id)
                        .first()
                    )

        else:
            # Perform RTMP IP Authorization Check
            authorized = checkRTMPAuthIP(request)
            if authorized[0] is False:
                return {
                    "results": {
                        "message": "Unauthorized RTMP Server or Missing User API Key - "
                        + authorized[1]
                    }
                }, 400

            channelData = cachedDbCalls.getChannelByLoc(channelEndpointID)

        if channelData is not None:
            restreamDestinationQuery = (
                Channel.restreamDestinations.query.filter_by(channel=channelData.id)
                .with_entities(
                    Channel.restreamDestinations.id,
                    Channel.restreamDestinations.channel,
                    Channel.restreamDestinations.name,
                    Channel.restreamDestinations.enabled,
                    Channel.restreamDestinations.url,
                )
                .all()
            )
            restreamDestinations = []
            for entry in restreamDestinationQuery:
                serialized = {
                    "id": entry.id,
                    "channel": templateFilters.get_channelLocationFromID(entry.channel),
                    "name": entry.name,
                    "enabled": entry.enabled,
                    "url": entry.url,
                }
                restreamDestinations.append(serialized)
            db.session.commit()
            return {"results": restreamDestinations}

        else:
            db.session.commit()
            return {"results": {"message": "Request Error"}}, 400
        

    @api.expect(channelRestreamPOST)
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def post(self, channelEndpointID):
        """Add a new restream destination for a channel"""
        # Check API Key
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers["X-API-KEY"]).first()
            if requestAPIKey is not None and requestAPIKey.isValid():
                channelData = (
                    Channel.Channel.query.filter_by(
                        channelLoc=channelEndpointID,
                        owningUser=requestAPIKey.userID,
                    )
                    .with_entities(Channel.Channel.id)
                    .first()
                )

                # Check if channel exists
                if channelData is None:
                    return {"results": "error", "reason": "channelNotFound"}

                # Get request arguments
                # args = request.json
                args = channelRestreamPOST.parse_args()

                # Create new restream destination
                new_restreamDestination = Channel.restreamDestinations(
                    channel=channelData.id,
                    name=args["name"],
                    url=args["url"]
                )

                enabled_str = args.get("enabled", "False")
                if enabled_str.lower() == "true":
                    new_restreamDestination.enabled = True
                else:
                    new_restreamDestination.enabled = False

                db.session.add(new_restreamDestination)
                db.session.commit()
                return {"results": {"message": "Restream destination successfully added"}}, 200
            
            else:
            # API key is invalid or not found
                return {"results": {"message": "Invalid or expired API key"}}, 400
            
        else:
            # API key is missing in the request headers
            return {"results": {"message": "Missing API key"}}, 400

            

            



    @api.expect(channelRestreamPUT)
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def put(self, channelEndpointID):
        """Updates an existing restream destination for a channel"""

        args = channelRestreamPUT.parse_args()

        # Check API Key
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(key=request.headers["X-API-KEY"]).first()
            if requestAPIKey is not None and requestAPIKey.isValid():
                channelData = (
                    Channel.Channel.query.filter_by(
                        channelLoc=channelEndpointID,
                        owningUser=requestAPIKey.userID,
                    )
                    .with_entities(Channel.Channel.id)
                    .first()
                )


                # Check if channel exists
                if channelData is not None:
                    # Get the restream destination to update
                    restreamDestination = Channel.restreamDestinations.query.filter_by(id=args["id"]).first()

                    if restreamDestination is not None:
                        # Update the restream destination fields
                        restreamDestination.name = args["name"]
                        restreamDestination.url = args["url"]

                        enabled_str = args.get("enabled", "False")
                        if enabled_str.lower() == "true":
                            restreamDestination.enabled = True
                        else:
                            restreamDestination.enabled = False
                        db.session.commit()
                        return {"results": {"message": "Restream destination successfully updated"}}, 200
                    else:
                        db.session.commit()
                        return {"results": {"message": "Request Error - No Such Restream Destination"}}, 400
                else:
                    db.session.commit()
                    return {"results": {"message": "Request Error - No Such Channel"}}, 400
            else:
                # API key is invalid or not found
                return {"results": {"message": "Invalid or expired API key"}}, 400
        else:
            # API key is missing in the request headers
            return {"results": {"message": "Missing API key"}}, 401
       



# Invites Endpoint for a Channel
@api.route("/<string:channelEndpointID>/invites")
@api.doc(security="apikey")
@api.doc(params={"channelEndpointID": "GUID Channel Location"})
class api_1_Invites(Resource):
    @api.expect(channelInviteGetInvite)
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def get(self, channelEndpointID):
        """
        Returns channel protection invites for a channel
        """
        args = channelInviteGetInvite.parse_args()
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    requestedChannel = None
                    if requestAPIKey.type == 1:
                        requestedChannel = Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID,
                            owningUser=requestAPIKey.userID,
                        ).first()
                        if requestedChannel is None:
                            db.session.commit()
                            db.session.close()
                            return {"results": {"message": "Unauthorized"}}, 401
                    elif requestAPIKey.type == 2:
                        requestedChannel = Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID
                        ).first()
                        if requestedChannel is None:
                            db.session.commit()
                            db.session.close()
                            return {
                                "results": {
                                    "message": "Request Error - No Such Channel"
                                }
                            }, 400
                    if requestedChannel is not None:
                        inviteReturnArray = {"results": []}
                        invitedUserQuery = []
                        if "userID" in args:
                            invitedUserQuery = invites.invitedViewer.query.filter_by(
                                channelID=requestedChannel.id,
                                userID=int(args["userID"]),
                            ).all()
                        else:
                            invitedUserQuery = invites.invitedViewer.query.filter_by(
                                channelID=requestedChannel.id
                            ).all()
                        for invite in invitedUserQuery:
                            inviteReturn = {
                                "id": invite.id,
                                "userID": invite.userId,
                                "addedDate": str(invite.addedDate),
                                "expiration": str(invite.expiration),
                                "inviteCode": invite.inviteCode,
                                "isValid": invite.isValid(),
                            }
                            inviteReturnArray["results"].append(inviteReturn)
                        return inviteReturnArray
                db.session.commit()
                db.session.close()
                return {"results": {"message": "Request Error - Expired API Key"}}, 401
        db.session.commit()
        return {"results": {"message": "Request Error"}}, 400

    def post(self, channelEndpointID):
        """
        Creates a new user invite for a channel
        """
        args = channelInvitePostInvite.parse_args()
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    requestedChannel = None
                    if requestAPIKey.type == 1:
                        requestedChannel = Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID,
                            owningUser=requestAPIKey.userID,
                        ).first()
                        if requestedChannel is None:
                            db.session.commit()
                            db.session.close()
                            return {"results": {"message": "Unauthorized"}}, 401
                    elif requestAPIKey.type == 2:
                        requestedChannel = Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID
                        ).first()
                        if requestedChannel is None:
                            db.session.commit()
                            db.session.close()
                            return {
                                "results": {
                                    "message": "Request Error - No Such Channel"
                                }
                            }, 400
                    if requestedChannel is not None:
                        if "userID" in args and "expirationDays" in args:
                            userQuery = Sec.User.query.filter_by(
                                id=int(args["userID"])
                            ).first()
                            if userQuery is not None:
                                newInvite = invites.invitedViewer(
                                    userQuery.id,
                                    requestedChannel.id,
                                    int(args["expirationDays"]),
                                )
                                db.session.add(newInvite)
                                db.session.commit()
                                db.session.close()
                                return {"results": {"message": "Success"}}
                            else:
                                db.session.commit()
                                db.session.close()
                                return {
                                    "results": {
                                        "message": "Request Error - Invalid User"
                                    }
                                }, 400
                    else:
                        db.session.commit()
                        db.session.close()
                        return {
                            "results": {"message": "Request Error - No Such Channel"}
                        }, 400
                else:
                    db.session.commit()
                    db.session.close()
                    return {
                        "results": {"message": "Request Error - Expired API Key"}
                    }, 401
        db.session.commit()
        return {"results": {"message": "Request Error"}}, 400

    def delete(self, channelEndpointID):
        """
        Deletes a user invite from a channel
        """
        args = channelInviteDeleteInvite.parse_args()
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    requestedChannel = None
                    if requestAPIKey.type == 1:
                        requestedChannel = Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID,
                            owningUser=requestAPIKey.userID,
                        ).first()
                        if requestedChannel is None:
                            db.session.commit()
                            db.session.close()
                            return {"results": {"message": "Unauthorized"}}, 401
                    elif requestAPIKey.type == 2:
                        requestedChannel = Channel.Channel.query.filter_by(
                            channelLoc=channelEndpointID
                        ).first()
                        if requestedChannel is None:
                            db.session.commit()
                            db.session.close()
                            return {
                                "results": {
                                    "message": "Request Error - No Such Channel"
                                }
                            }, 400
                    if requestedChannel is not None:
                        if "userID" in args:
                            inviteQuery = invites.invitedViewer.query.filter_by(
                                channelID=requestedChannel.id, user=int(args["userID"])
                            ).first()
                            if inviteQuery != None:
                                db.session.delete(inviteQuery)
                                db.session.commit()
                                db.session.close()
                                return {"results": {"message": "Success"}}
                            else:
                                db.session.commit()
                                db.session.close()
                                return {
                                    "results": {
                                        "message": "Request Error - Invalid User"
                                    }
                                }, 400
                    else:
                        db.session.commit()
                        db.session.close()
                        return {
                            "results": {"message": "Request Error - No Such Channel"}
                        }, 400
                else:
                    db.session.commit()
                    db.session.close()
                    return {
                        "results": {"message": "Request Error - Expired API Key"}
                    }, 401
        db.session.commit()
        return {"results": {"message": "Request Error"}}, 400


@api.route("/authed/")
class api_1_ListChannelAuthed(Resource):
    @api.doc(security="apikey")
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def get(self):
        """
        Gets an authenticated view of the settings of all owned Channels
        """
        if "X-API-KEY" in request.headers:
            requestAPIKey = apikey.apikey.query.filter_by(
                key=request.headers["X-API-KEY"]
            ).first()
            if requestAPIKey is not None:
                if requestAPIKey.isValid():
                    channelQuery = Channel.Channel.query.filter_by(
                        owningUser=requestAPIKey.userID
                    ).all()
                    if channelQuery != []:
                        db.session.commit()
                        return {
                            "results": [ob.authed_serialize() for ob in channelQuery]
                        }
        return {"results": {"message": "Request Error"}}, 400


@api.route("/search")
class api_1_SearchChannels(Resource):
    # Channel - Search Channels
    @api.expect(channelSearchPost)
    @api.doc(responses={200: "Success", 400: "Request Error"})
    def post(self):
        """
        Searches Channel Names and Metadata and returns Name and Link
        """
        args = channelSearchPost.parse_args()
        finalArray = []
        if "term" in args:
            returnArray = cachedDbCalls.searchChannels(args["term"])
            for chan in returnArray:
                newChanObj = [chan.id, chan.channelName, chan.channelLoc, chan.imageLocation]
                finalArray.append(newChanObj)
            return {"results": finalArray}
        else:
            return {"results": {"message": "Request Error"}}, 400
