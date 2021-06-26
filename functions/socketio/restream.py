from flask import abort, current_app, request
from flask_socketio import emit
from flask_security import current_user

from classes.shared import db, socketio
from classes import Channel
from classes import settings
from functions import system
from classes import Sec
from classes import settings
import socket

@socketio.on('newRestream')
def newRestream(message):
    restreamChannel = message['restreamChannelID']
    channelQuery = Channel.Channel.query.filter_by(id=int(restreamChannel)).first()
    if channelQuery is not None:
        if channelQuery.owningUser == current_user.id:
            restreamName = message['name']
            restreamURL = message['restreamURL']

            url = restreamURL.lower()
            sysSettings = settings.getSettingsFromRedis()
          
            userQuery = Sec.User.query.filter_by(id=int(channelQuery.owningUser)).with_entities(Sec.User.username, Sec.User.verified).first()
            count = Channel.restreamDestinations.query.filter_by(channel=channelQuery.id).count()
            theUserName = userQuery.username          
            
            externalIP = socket.gethostbyname(sysSettings.siteAddress)
                    
            if ("127.0.0.1" in url or externalIP in url or sysSettings.siteAddress.lower() in url or "localhost" in url) == True:
                system.newLog(1, "***** WARNING Restream config USER ATTACK??? ***** " + theUserName + "tried to add = " + url) 
                db.session.commit()
                db.session.close()
                return abort(401)

            if count > 0 and userQuery.verified==0:            
                system.newLog(1, "Restream config: " + theUserName + " tried to add = " + url) 
                db.session.commit()
                db.session.close()
                return abort(401)

            if count >= 8:  # sets max restreams a verified user can have
                system.newLog(1, "Restream config: " + theUserName + " tried to add too many restreams = " + url) 
                db.session.commit()
                db.session.close()
                return abort(401)

            count = Channel.restreamDestinations.query.filter_by(channel=channelQuery.id, url= restreamURL).count()
            if count > 0:
                system.newLog(1, "Restream config: " + theUserName + " tried to duplicate restreams = " + url) 
                db.session.commit()
                db.session.close()
                return abort(401)

            system.newLog(1, "Restream config: " + theUserName + " added = " + url +" Your IP= " + externalIP) 

            newRestreamObject = Channel.restreamDestinations(channelQuery.id, restreamName, url)

            db.session.add(newRestreamObject)
            db.session.commit()

            restreamQuery = Channel.restreamDestinations.query.filter_by(name=restreamName, url=restreamURL, channel=int(restreamChannel), enabled=False).first()
            restreamID = restreamQuery.id

            emit('newRestreamAck', {'restreamName': restreamName, 'restreamURL': restreamURL, 'restreamID': str(restreamID), 'channelID': str(restreamChannel)}, broadcast=False)
        else:
            db.session.commit()
            db.session.close()
            return abort(401)
    else:
        db.session.commit()
        db.session.close()
        return abort(500)
    db.session.commit()
    db.session.close()
    return 'OK'

@socketio.on('toggleRestream')
def toggleRestream(message):
    restreamID = message['id']
    restreamQuery = Channel.restreamDestinations.query.filter_by(id=int(restreamID)).first()
    if restreamQuery is not None:
        if restreamQuery.channelData.owningUser == current_user.id:
            restreamQuery.enabled = not restreamQuery.enabled
            db.session.commit()
        else:
            db.session.commit()
            db.session.close()
            return abort(401)
    else:
        db.session.commit()
        db.session.close()
        return abort(500)
    db.session.commit()
    db.session.close()
    return 'OK'

@socketio.on('deleteRestream')
def deleteRestream(message):
    restreamID = message['id']
    restreamQuery = Channel.restreamDestinations.query.filter_by(id=int(restreamID)).first()
    if restreamQuery is not None:
        if restreamQuery.channelData.owningUser == current_user.id:
            db.session.delete(restreamQuery)
            db.session.commit()
        else:
            db.session.commit()
            db.session.close()
            return abort(401)
    else:
        db.session.commit()
        db.session.close()
        return abort(500)
    db.session.commit()
    db.session.close()
    return 'OK'