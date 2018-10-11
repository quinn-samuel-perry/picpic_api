#!/usr/bin/env python2

import requests
from requests_toolbelt import MultipartEncoder
import json
import subprocess
import re
import mimetypes

class Session():
    def __init__(s):
        s.token       =  None
        s.username    = 
        s.password    = 
        s.url         = 'http://cloud.picpicsocial.com/'
        s.ppversion   = '2.6.9.6' #just what im currently using
        s.authenticity_token = None
        s.api_url     = s.url + 'api/v1/'
        s.seshId      = None
        s.cookies     = None
        s.param_def   = {}

    def add_dicts(s,dict1,dict2):
        #lazy way to add two dicts together
        return dict(dict1.items() + dict2.items())

    def debug_print(s, msg):
        print '[*]',msg

    def pretty_json(s,j):
        return json.dumps(j,indent=4,sort_keys=True)

    def nab_token(s,r):
        #turns out there's two authenticity_token values. only one is important
        #m = re.search( r'.*name="authenticity_token" value="(.*)".*', r, re.M|re.I)
        #s.authenticity_token = m.group(1)
        m = re.search( r'.*name="csrf-token" content="(.*)".*', r)
        s.authenticity_token = m.group(1)
        return

    def login(s):
        s.debug_print('fetching log in page...')
        url = s.url + 'sign_in/'
        
        r = requests.get(url)
        r.raise_for_status()
        s.cookies = r.cookies
        s.debug_print('nabbing authenticity_token..')
        s.nab_token(r.content)
        s.debug_print('nabbed authenticity_token')
        
        s.debug_print('logging in')
        params = { }
        payload = { 'utf8' : '%E2%9C%93','authenticity_token':s.authenticity_token,
                    'user[email]':s.username,
                    'user[password]':s.password,
                    'commit':'Sign+in',}
        
        r = requests.post(url,data=payload,cookies=s.cookies)
        r.raise_for_status()
       	
	#looking at this 1 year later, this is absolutely horrendous  
        if re.search( r'.*<title>(.*)</title>',r.content).group(1) == "Events dashboard - Picpic":
            s.debug_print('login successful')
        return True

    def getTime(s):
        s.debug_print('getting time')
        
        url = s.api_url + 'subscription/time.json'

        params = s.add_dicts({},s.param_def)
        
        r = requests.get(url,params=params)
        j = r.json()
        
        #print s.pretty_json(j)
        return j['time']

    def getTokens(s):
        s.debug_print('getting token for more api requests...')

        url = s.api_url + 'tokens.json'
        params = s.add_dicts({'email':s.username,'password':s.password,'version':s.ppversion},s.param_def)
        
        r = requests.post(url,params=params,cookies=s.cookies)
        
        j = r.json()

        s.token = j['token']
        return j['token']

    #returns remaining events,
    #       published events,
    #       renewal date,
    #       and status
    def getSubscriptionStatus(s):
        s.debug_print('getting subscription status...')
        
        url = s.api_url + 'subscription.json'
        params = s.add_dicts({'token':s.token},s.param_def)
        
        r = requests.get(url,params=params)
        j = r.json()
        
        print s.pretty_json(j)
        return j['events_remaining'],j['published_events'],j['renew_date'],j['status']

    def getEvents(s):
        s.debug_print('getting events...')
        
        url = s.api_url + 'events.json'

        params = {'token':s.token}

        r = requests.get(url,params=params)
        j = r.json()
        
        #print s.pretty_json(j)
        events = []
        for d in j:
            events.append(d['id'])
        
        return len(events), events

    def getEventDetails(s,id):
        id=str(id)
        s.debug_print('getting event %s details..' % id)
        
        url = s.api_url + 'events/' + id+ '.json'

        params = {'token':s.token}

        r = requests.get(url,params=params)
        j = r.json()
        
        print s.pretty_json(j)
        
    def uploadPhoto(s,id,photo):
        id=str(id)
        s.debug_print('attempting to upload %s to event %s' %( id, photo))
        
        url = s.api_url + 'photos.json'
        
        files = { 'token':      (None, s.token),
                    'event_id': (None, id),
                    'image':    (photo, open(photo,'rb'),mimetypes.guess_type(photo)[0])}
        
        #need to use MultipartEncoder to properly set boundary. 
        #this isn't necessary, and it works without this boundary,
        #but this is what 2.6.9.6 uses as their setting, so I figured 
        #it couldn't hurt. Useragent also matches :)
        m = MultipartEncoder(files,boundary='-----------------------------28947758029299')
        headers = {'User-Agent':'RestSharp/105.2.3.0',
                'Content-Type': m.content_type,}

        r = requests.post(url,headers=headers,data=m.to_string())
        #print r.headers
        #print r.text
        print r.content
        return
