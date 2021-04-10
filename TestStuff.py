# -*- coding: UTF-8 -*-
#from gevent import monkey
#monkey.patch_all(thread=True)

from flask import Flask
from conf import config

from classes import Stream
from classes import upvotes
from classes import comments
from classes import invites
from classes import webhook
from classes import subscriptions
from classes import notifications
from classes import stickers
from functions import database
from functions import system
from classes.shared import db

from globals import globalvars
from classes import RecordedVideo
import os

from pathlib import Path
import glob

from classes import Channel
from classes.Sec import User


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Begin Database Initialization
db.init_app(app)
db.app = app

#system.newLog(0, "Testing Stuff")

fred = "{}{}".format("fred ","boggs")

print(fred)
