#! /usr/bin/env python2
import picpic

sesh = picpic.Session()

if not sesh.login():
	print '[-] Could not login\n'

sesh.getTokens()
sesh.getSubscriptionStatus()
count, events = sesh.getEvents()


for e in events:
	sesh.getEventDetails(e)
    sesh.uploadPhoto(e,'truck.jpg')