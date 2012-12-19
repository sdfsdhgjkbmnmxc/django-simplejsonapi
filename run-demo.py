#!/usr/bin/python
import urllib2
from django.utils import simplejson

data = simplejson.dumps({
    "action": "ping",
    "params": {},
})
content = urllib2.urlopen('http://127.0.0.1:5656', data).read()
print simplejson.loads(content)
