django-simplejsonapi
====================

Install
```
pip install -e git+git://github.com/sdfsdhgjkbmnmxc/django-simplejsonapi.git#egg=simplejsonapi
```

Setup settings.py
```python 
INSTALLED_APPS = (
    # ....
    'simplejsonapi',
)
```

Run:
```
./manage.py run_jsonapi_server --host=127.0.0.1 --port=5656
```

Try
```python
>>> import urllib2
>>> from django.utils import simplejson
>>> data = simplejson.dumps({"action": "ping", "params": {}})
>>> content = urllib2.urlopen('127.0.0.1:5656', data).read()
>>> simplejson.loads(content)
{u'_time': u'0.0004', u'result': u'pong'}

```

Usage in any always imported python file:
```python 
from simplejsonapi import register_action 

@register_action
def my_func(k)
    return {
        'k': k,
        'k ** 2': k * k,
    }
```
