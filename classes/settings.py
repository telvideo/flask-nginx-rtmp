from .shared import db

class settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    siteName = db.Column(db.String(255))
    siteProtocol = db.Column(db.String(24))
    siteAddress = db.Column(db.String(255))
    smtpAddress = db.Column(db.String(255))
    smtpPort = db.Column(db.Integer)
    smtpTLS = db.Column(db.Boolean)
    smtpSSL = db.Column(db.Boolean)
    smtpUsername = db.Column(db.String(255))
    smtpPassword = db.Column(db.String(255))
    smtpSendAs = db.Column(db.String(255))
    allowRecording = db.Column(db.Boolean)
    allowUploads = db.Column(db.Boolean)
    protectionEnabled = db.Column(db.Boolean)
    adaptiveStreaming = db.Column(db.Boolean)
    background = db.Column(db.String(255))
    showEmptyTables = db.Column(db.Boolean)
    allowComments = db.Column(db.Boolean)
    systemTheme = db.Column(db.String(255))
    systemLogo = db.Column(db.String(255))
    version = db.Column(db.String(255))
    sortMainBy = db.Column(db.Integer)
    restreamMaxBitrate = db.Column(db.Integer)
    serverMessageTitle = db.Column(db.String(256))
    serverMessage = db.Column(db.String(8192))
    maxClipLength = db.Column(db.Integer)
    proxyFQDN = db.Column(db.String(2048))
    maintenanceMode = db.Column(db.Boolean)
    buildEdgeOnRestart = db.Column(db.Boolean)
    allowRegistration = db.Column(db.Boolean) # Moved to config.py
    requireConfirmedEmail = db.Column(db.Boolean) # Moved to config.py

    def __init__(self, siteName, siteProtocol, siteAddress, smtpAddress, smtpPort, smtpTLS, smtpSSL, smtpUsername, smtpPassword, smtpSendAs, allowRecording, allowUploads, adaptiveStreaming, showEmptyTables, allowComments, version):
        self.siteName = siteName
        self.siteProtocol = siteProtocol
        self.siteAddress = siteAddress
        self.smtpAddress = smtpAddress
        self.smtpPort = smtpPort
        self.smtpTLS = smtpTLS
        self.smtpSSL = smtpSSL
        self.smtpUsername = smtpUsername
        self.smtpPassword = smtpPassword
        self.smtpSendAs = smtpSendAs
        self.allowRecording = allowRecording
        self.allowUploads = allowUploads
        self.adaptiveStreaming = adaptiveStreaming
        self.showEmptyTables = showEmptyTables
        self.allowComments = allowComments
        self.sortMainBy = 0
        self.background = "Ash"
        self.systemTheme = "Defaultv2"
        self.version = version
        self.systemLogo = "/static/img/logo.png"
        self.serverMessageTitle = "Server Message"
        self.serverMessage = ""
        self.restreamMaxBitrate = 3500
        self.maxClipLength = 90
        self.buildEdgeOnRestart = True
        self.protectionEnabled = False
        self.maintenanceMode = False

    def __repr__(self):
        return '<id %r>' % self.id

    def serialize(self):
        return {
            'siteName': self.siteName,
            'siteProtocol': self.siteProtocol,
            'siteAddress': self.siteAddress,
            'siteURI': self.siteProtocol + self.siteAddress,
            'siteLogo': self.systemLogo,
            'serverMessageTitle': self.serverMessageTitle,
            'serverMessage': self.serverMessage,
            'allowRecording': self.allowRecording,
            'allowUploads': self.allowUploads,
            'allowComments': self.allowComments,
            'version': self.version,
            'restreamMaxBitRate': self.restreamMaxBitrate,
            'maxClipLength': self.maxClipLength,
            'protectionEnabled': self.protectionEnabled,
            'adaptiveStreaming': self.adaptiveStreaming,
            'maintenanceMode': self.maintenanceMode
        }
###

import redis

from flask_redis import FlaskRedis

r = FlaskRedis(decode_responses=True)

def setupRedis(theapp):
    r.init_app(theapp)

# refill the redis from the database and tell everyone that they need to refresh their version of the redis
def informRedisOfUpdate():
    fillRedis()
    rTest = r.get('OSP REDIS')
    if rTest ==  None:                              
        rTest=1
    rTest = int(rTest) +1   # Add one so that all processes (and ours) notice that they need to refresh their global version of redis
    r.set('OSP REDIS',int(rTest)) 

# Fill redis with data read from database.  Called once at startup and whenever informRedisOfUpdate() is called
def fillRedis():

    lsysSettings = settings.query.first()       #get real data from database using local handle

    r.set("id", lsysSettings.id)
    r.set("siteName", lsysSettings.siteName)
    r.set("siteProtocol", lsysSettings.siteProtocol)
    r.set("siteAddress", lsysSettings.siteAddress)
    r.set("smtpAddress", lsysSettings.smtpAddress)
    r.set("smtpPort", lsysSettings.smtpPort)
    r.set("smtpTLS", int(lsysSettings.smtpSSL))
    r.set("smtpSSL", int(lsysSettings.smtpSSL))
    r.set("smtpUsername", lsysSettings.smtpUsername)
    r.set("smtpPassword", lsysSettings.smtpPassword)
    r.set("smtpSendAs", lsysSettings.smtpSendAs)
    r.set("allowRecording", int(lsysSettings.allowRecording))
    r.set("allowUploads", int(lsysSettings.allowUploads))
    r.set("protectionEnabled", int(lsysSettings.protectionEnabled))
    r.set("adaptiveStreaming", int(lsysSettings.adaptiveStreaming))
    r.set("background", lsysSettings.background)
    r.set("showEmptyTables", int(lsysSettings.showEmptyTables))
    r.set("allowComments", int(lsysSettings.allowComments))
    r.set("systemTheme", lsysSettings.systemTheme)
    r.set("systemLogo", lsysSettings.systemLogo)
    r.set("version", lsysSettings.version)
    r.set("sortMainBy", lsysSettings.sortMainBy)
    r.set("restreamMaxBitrate", lsysSettings.restreamMaxBitrate)
    r.set("serverMessageTitle", lsysSettings.serverMessageTitle)
    r.set("serverMessage", lsysSettings.serverMessage)
    r.set("maxClipLength", lsysSettings.maxClipLength)

    #r.set("proxyFQDN", sysSettings.proxyFQDN)
    if lsysSettings.proxyFQDN == None:
        r.set("proxyFQDN", "None")
    else:
        r.set("proxyFQDN", lsysSettings.proxyFQDN)

    r.set("maintenanceMode", int(lsysSettings.maintenanceMode))
    r.set("buildEdgeOnRestart", int(lsysSettings.buildEdgeOnRestart))

    #r.set("allowRegistration", int(sysSettings.allowRegistration))
    if lsysSettings.allowRegistration == None:
        r.set("allowRegistration", 0)
    else:
        r.set("allowRegistration", int(lsysSettings.allowRegistration))
    #r.set("requireConfirmedEmail", int(sysSettings.requireConfirmedEmail))
    if lsysSettings.requireConfirmedEmail == None:
        r.set("requireConfirmedEmail", 0)
    else:
        r.set("requireConfirmedEmail", int(lsysSettings.requireConfirmedEmail))

# Globals used to store a copy of redis data so we don't need to load it from Redis every time
gsysSettings = settings("Resis Not set","","","",0,0,0,0,0,0,0,0,0,0,0,0)   # Do not use gsysSettings as part of any actual database call or it will break sql 
gsysSettingsCounter = int(0)

# Globals used to store a copy of data, now we need to restart osp.target if we change rtmpserver...
grtmpServerSettings = []

gAuthSettingsList = []
gAuthFlag = True

def getSettingsFromRedis():
    global gsysSettings
    global gsysSettingsCounter

    #msysSettings = settings.query.first()          # remove two comments to not use redis for settings
    #return(msysSettings)

    rTest = r.get('OSP REDIS')
    if rTest ==  None:                              
        fillRedis()                                 # create redis if not there
        r.set('OSP REDIS',int(1))                   # set initial value
        rTest=1

    rTest = int(rTest)
    if rTest == gsysSettingsCounter:                # if someone else has not changed them...
        return(gsysSettings)                        # return our global copy

    # setting must have changed so get them
    
    gsysSettingsCounter = rTest                     # so we don't get them all again next time

    #gsysSettings = settings("Resis Not set","","","",0,0,0,0,0,0,0,0,0,0,0,0)    
    gsysSettings.id = int(r.get("id"))
    gsysSettings.siteName = r.get("siteName")
    gsysSettings.siteProtocol = r.get("siteProtocol")
    gsysSettings.siteAddress = r.get("siteAddress")
    gsysSettings.smtpAddress = r.get("smtpAddress")
    gsysSettings.smtpPort = int(r.get("smtpPort"))
    gsysSettings.smtpTLS = int(r.get("smtpTLS"))
    gsysSettings.smtpSSL = int(r.get("smtpSSL"))
    gsysSettings.smtpUsername = r.get("smtpUsername")
    gsysSettings.smtpPassword = r.get("smtpPassword")
    gsysSettings.smtpSendAs = r.get("smtpSendAs") 
    gsysSettings.allowRecording = bool(int(r.get("allowRecording")))
    gsysSettings.allowUploads = bool(int(r.get("allowUploads")))
    gsysSettings.protectionEnabled = bool(int(r.get("protectionEnabled")))
    gsysSettings.adaptiveStreaming = bool(int(r.get("adaptiveStreaming")))
    gsysSettings.background = r.get("background") 
    gsysSettings.showEmptyTables = bool(int(r.get("showEmptyTables")))
    gsysSettings.allowComments = bool(int(r.get("allowComments")))
    gsysSettings.systemTheme = r.get("systemTheme") 
    gsysSettings.systemLogo = r.get("systemLogo") 
    gsysSettings.version = r.get("version") 
    gsysSettings.sortMainBy = int(r.get("sortMainBy")) 
    gsysSettings.restreamMaxBitrate = int(r.get("restreamMaxBitrate")) 
    gsysSettings.serverMessageTitle = r.get("serverMessageTitle") 
    gsysSettings.serverMessage = r.get("serverMessage") 
    gsysSettings.maxClipLength = int(r.get("maxClipLength"))

    proxyFQDN = r.get("proxyFQDN") 

    if proxyFQDN == "None":
        gsysSettings.proxyFQDN = None
    else:
        gsysSettings.proxyFQDN = proxyFQDN

    gsysSettings.maintenanceMode = bool(int(r.get("maintenanceMode")))
    gsysSettings.buildEdgeOnRestart = bool(int(r.get("buildEdgeOnRestart")))

    gsysSettings.allowRegistration = bool(int(r.get("allowRegistration")))
    gsysSettings.requireConfirmedEmail = bool(int(r.get("requireConfirmedEmail")))

    #r.set("allowRegistration", int(sysSettings.allowRegistration)) if these are not working we might need something like this?
#    if sysSettings.allowRegistration == None:
#        r.set("allowRegistration", 0)
#    else:
#        r.set("allowRegistration", int(sysSettings.allowRegistration))
#    #r.set("requireConfirmedEmail", int(sysSettings.requireConfirmedEmail))
#    if sysSettings.requireConfirmedEmail == None:
#        r.set("requireConfirmedEmail", 0)
#    else:
#        r.set("requireConfirmedEmail", int(sysSettings.requireConfirmedEmail))

    return(gsysSettings)

####
class edgeStreamer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(1024))
    port = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    status = db.Column(db.Integer)
    loadPct = db.Column(db.Integer)

    def __init__(self, address, port, loadPct):
        self.address = address
        self.active = False
        self.status = 0
        self.port = port
        self.loadPct = loadPct

    def __repr__(self):
        return '<id %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'address': self.address,
            'port': self.port,
            'active': self.active,
            'status': self.status,
            'loadPct': self.loadPct
        }

class rtmpServer(db.Model):
    __tablename__ = "rtmpServer"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(1024))
    active = db.Column(db.Boolean)
    streams = db.relationship('Stream', backref='server', cascade="all, delete-orphan", lazy="joined")

    def __init__(self, address):
        self.address = address
        self.active = True

    def __repr__(self):
        return '<id %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'address': self.address,
            'active': self.active
        }

class oAuthProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    friendlyName = db.Column(db.String(64))
    preset_auth_type = db.Column(db.String(64))
    displayColor = db.Column(db.String(8))
    client_id = db.Column(db.String(256))
    client_secret = db.Column(db.String(256))
    access_token_url = db.Column(db.String(1024))
    access_token_params = db.Column(db.String(1024))
    authorize_url = db.Column(db.String(1024))
    authorize_params = db.Column(db.String(1024))
    api_base_url = db.Column(db.String(1024))
    client_kwargs = db.Column(db.String(2056))
    profile_endpoint = db.Column(db.String(2056))
    id_value = db.Column(db.String(256))
    username_value = db.Column(db.String(256))
    email_value = db.Column(db.String(256))

    def __init__(self, name, preset_auth_type, friendlyName, displayColor, client_id, client_secret, access_token_url, authorize_url, api_base_url, profile_endpoint, id_value, username_value, email_value):
        self.name = name
        self.preset_auth_type = preset_auth_type
        self.friendlyName = friendlyName
        self.displayColor = displayColor
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_url = access_token_url
        self.authorize_url = authorize_url
        self.api_base_url = api_base_url
        self.profile_endpoint = profile_endpoint
        self.id_value = id_value
        self.username_value = username_value
        self.email_value = email_value

    def __repr__(self):
        return '<id %r>' % self.id

#from functions import system

def getAuthProvider(calledby):
    global gAuthSettingsList
    global gAuthFlag 

    #return oAuthProvider.query.all()

    if gAuthFlag == True:
        # system.newLog(1, "getAuthProvider BY= ")   
        gAuthFlag = False
        tOAuthProvidersList = oAuthProvider.query.all()
        for p in tOAuthProvidersList:
            newOauthProvider = oAuthProvider( p.name,p.preset_auth_type, p.friendlyName, p.displayColor, p.client_id, p.client_secret, p.access_token_url, p.authorize_url, p.api_base_url, p.profile_endpoint, p.id_value, p.username_value, p.email_value)

            newOauthProvider.id = p.id
            newOauthProvider.access_token_params = p.access_token_params
            newOauthProvider.authorize_params = p.authorize_params
            newOauthProvider.client_kwargs = p.client_kwargs

            gAuthSettingsList.append(newOauthProvider)

    return gAuthSettingsList



def getrtmpServer(calledby ):
    global grtmpServerSettings

    #system.newLog(1, "getrtmpServer BY= " + calledby) 
    
    #rList = rtmpServer.query.all()
    #return (rList )

    if (grtmpServerSettings == []):
        tempServerSettingsList = rtmpServer.query.all() 

        for server in tempServerSettingsList:
            newServer = rtmpServer(server.address)
            newServer.id = server.id
            newServer.active = server.active
            newServer.address = server.address

            grtmpServerSettings.append(newServer)

#    for server in grtmpServerSettings:
#        count =count + 1
#        outs =  str(count) + " " + server.address +  " id " + str(server.id) + " AC " + str(server.active)
       # system.newLog(1, "DEBUG = " + outs)

    return(grtmpServerSettings)