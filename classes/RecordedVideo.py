from .shared import db

class RecordedVideo(db.Model):
    __tablename__ = "RecordedVideo"
    id = db.Column(db.Integer,primary_key=True)
    videoDate = db.Column(db.DateTime)
    owningUser = db.Column(db.Integer,db.ForeignKey('user.id'))
    channelName = db.Column(db.String(255))
    channelID = db.Column(db.Integer,db.ForeignKey('Channel.id'))
    description = db.Column(db.String(2048))
    topic = db.Column(db.Integer)
    views = db.Column(db.Integer)
    length = db.Column(db.Float)
    videoLocation = db.Column(db.String(255))
    thumbnailLocation = db.Column(db.String(255))
    pending = db.Column(db.Boolean)
    allowComments = db.Column(db.Boolean)
    upvotes = db.relationship('videoUpvotes', backref='recordedVideo', cascade="all, delete-orphan", lazy="joined")
    comments = db.relationship('videoComments', backref='recordedVideo', cascade="all, delete-orphan", lazy="joined")
    clips = db.relationship('Clips', backref='recordedVideo', cascade="all, delete-orphan", lazy="joined")

    def __init__(self, owningUser, channelID, channelName, topic, views, videoLocation, videoDate, allowComments):
        self.videoDate = videoDate
        self.owningUser = owningUser
        self.channelID = channelID
        self.channelName = channelName
        self.topic = topic
        self.views = views
        self.videoLocation = videoLocation
        self.pending = True
        self.allowComments = allowComments

    def __repr__(self):
        return '<id %r>' % self.id

    def get_upvotes(self):
        return len(self.upvotes)

    def serialize(self):
        return {
            'id': self.id,
            'channelID': self.channelID,
            'owningUser': self.owningUser,
            'videoDate': str(self.videoDate),
            'videoName': self.channelName,
            'description': self.description,
            'topic': self.topic,
            'views': self.views,
            'length': self.length,
            'upvotes': self.get_upvotes(),
            'videoLocation': '/videos/' + self.videoLocation,
            'thumbnailLocation': '/videos/' + self.thumbnailLocation,
            'ClipIDs': [obj.id for obj in self.clips],
        }

class Clips(db.Model):
    __tablename__ = "Clips"
    id = db.Column(db.Integer, primary_key=True)
    parentVideo = db.Column(db.Integer, db.ForeignKey('RecordedVideo.id'))
    startTime = db.Column(db.Float)
    endTime = db.Column(db.Float)
    length = db.Column(db.Float)
    views = db.Column(db.Integer)
    clipName = db.Column(db.String(255))
    description = db.Column(db.String(2048))
    thumbnailLocation = db.Column(db.String(255))
    upvotes = db.relationship('clipUpvotes', backref='clip', cascade="all, delete-orphan", lazy="joined")

    def __init__(self, parentVideo, startTime, endTime, clipName, description):
        self.parentVideo = parentVideo
        self.startTime = startTime
        self.endTime = endTime
        self.description = description
        self.clipName = clipName
        self.length = endTime-startTime
        self.views = 0

    def __repr__(self):
        return '<id %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'parentVideo': self.parentVideo,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'length': self.length,
            'name': self.clipName,
            'description': self.description,
            'views': self.views,
            'thumbnailLocation': '/videos/' + self.thumbnailLocation
        }