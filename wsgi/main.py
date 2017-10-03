# -- coding: utf-8 --
""" 
Basic blog using webpy 0.3 
Heavily modified by hakanu:
 * renamed classes and models and templates
 * add config.py to isolate configuration settings
 * add authentication features
 * added jinja2 templating instead of default webpy.
"""
import os
import re
import json
import sys

import web
import requests


urls = (
    '/.*', 'FrontPageHandler',
)

_DEBUG = False
_WEBSITE_ADDRESS = 'http://guldumnet.tumblr.com'
_MIRROR_ADDRESS = 'http://guldum.net'
if _DEBUG:
  _MIRROR_ADDRESS = 'http://localhost:8080'
_MOBILE_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'

class FrontPageHandler:
  def GET(self):
    suburl = ''
    try:
      # If this blog runs, it's highly likely it's on openshift.
      # Otherwise it falls back to normal localhost mode.
      # For openshift this is needed, otherwise it renders html as raw text.
      web.header('Content-Type','text/html; charset=utf-8', unique=True)
      suburl = web.ctx.env['PATH_INFO']
    except Exception, e:
      print 'Exception occurred: ', e
      suburl = web.ctx.path + web.ctx.query
    request_url = _WEBSITE_ADDRESS + suburl 
    print 'request_url: ', request_url
    # Need headers to understand if request is coming from mobile.
    #print 'web.ctx.env: ', web.ctx.env
    user_agent = web.ctx.env['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in web.ctx.env else _MOBILE_USER_AGENT
    headers = {'user-agent': user_agent}
    result = requests.get(request_url, headers=headers)
    print result.status_code
    if result.status_code == 200:
      content = result.text
      # Change the links as well.
      content = content.replace(
          _WEBSITE_ADDRESS.replace('http://', 'https://'), _MIRROR_ADDRESS)
      content = content.replace(_WEBSITE_ADDRESS, _MIRROR_ADDRESS)
      return content
    else:
      return '<a href="http://guldum.net">Working!</a>'
      #raise web.seeother('/')


############# MAIN
application = web.application(urls, globals())

web.action = ''

#if __name__ == "__main__":
print 'Arguments: ', sys.argv
# rhc env set DEV_MODE=0  -a webpy
# heroku config:set DEV_MODE=0 --app paylasio
if 'DEV_MODE' in os.environ and os.environ['DEV_MODE'] == '1':
  print 'Debug mode on!!!'
  #config.init()
elif 'DEV_MODE' in os.environ and os.environ['DEV_MODE'] == '0':
  print 'Debug mode off!!!'
  #config.init(is_debug=False)
  web.debug = False
  web.config.debug = False
else:
  print 'DEV_MODE is not specified in the env variables so assuming its ON'
  print 'Debug mode on!!!'
  #config.init()

# For logging purposes. Debug logs are going to a separate parse app.
if not web.debug:
  # TODO(hakanu): Only activate logging hooks if it's prod.
  application.add_processor(_LogSaver)  # Before and after handling hooks.
else:
  print 'Sudo connecting to parse.'

ip = ''
port = 8080
host_name = 'localhost'
is_openshift = False
app = application
try:
  ########## OPENSHIFT
  ip = os.environ['OPENSHIFT_PYTHON_IP']
  port = int(os.environ['OPENSHIFT_PYTHON_PORT'])
  host_name = os.environ['OPENSHIFT_GEAR_DNS']
  session_dir = os.environ['OPENSHIFT_TMP_DIR'] + '/sessions'
  #logger = logging.getLogger('prodLogger')
  print '=========OPENSHIFT MODE ON!==========='
  print 'ip: ', ip
  print 'port: ', port
  print 'host_name: ', host_name
  is_openshift = True
  application = application.wsgifunc()
  ########### /OPENSHIFT
except:
  print '=========OPENSHIFT MODE OFF!==========='
  is_openshift = False

# Set up loggly.
logger = None
try:
  # Logging.
  import logging
  import logging.config
  import loggly.handlers
  logging.config.fileConfig(
      os.path.join(os.path.dirname(__file__), 'loggly.conf'))
  if not is_openshift:
    logger = logging.getLogger('devLogger')
  else:
    logger = logging.getLogger('prodLogger')
except Exception, e:
  print 'Loggly installation failed, going without loggly: ', e

if __name__ == '__main__':
  if not is_openshift:
    application.run()
############################################################ /Main func.

