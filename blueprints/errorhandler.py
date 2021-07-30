from flask import Blueprint, request, render_template

from classes import settings

from functions import themes
from functions import system
import datetime

errorhandler_bp = Blueprint('errors', __name__)

@errorhandler_bp.app_errorhandler(404)
def page_not_found(e):
    #sysSettings = settings.settings.query.first()
    #sysSettings = settings.getSettingsFromRedis()    
    #system.newLog(0, "404 (420) Error - " + str(request.url))

    tDate = datetime.datetime.utcnow()

    stri ="420 {} {} {} \n".format(tDate, request.referrer, request.url)

    f = open("/var/www/420dicks.txt", "a")
    f.write(stri)
    f.close()

    return "404 Error.", 404
    #return render_template(themes.checkOverride('404.html'), sysSetting=sysSettings, previous=request.referrer), 404

@errorhandler_bp.app_errorhandler(500)
def page_not_found(e):
    #sysSettings = settings.settings.query.first()
    #sysSettings = settings.getSettingsFromRedis()    
    system.newLog(0,"500 Error - " + str(request.url))
    return "500 Error. Who lost that page? Take a break and try again later maybe?", 500

#    return render_template(themes.checkOverride('500.html'), previous=request.referrer, error=e), 500