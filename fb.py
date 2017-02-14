# coding: utf-8

import facebook
import urllib 
import urlparse

with open('fbt','r') as f:
    access_token_page = f.read()
FACEBOOK_APP_ID = '1554121884880058'

oauth_args = dict(client_id     = FACEBOOK_APP_ID,
                  grant_type    = 'client_credentials')

#oauth_response = urllib.urlopen('https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)).read()                                  

attach = {
  "name": 'Hello world',
  "link": 'http://www.example.com',
  "caption": 'test post',
  "description": 'some test',
}


facebook_graph = facebook.GraphAPI(access_token_page)
try:
    response = facebook_graph.put_wall_post('', attachment=attach)
except facebook.GraphAPIError as e:
    print e
