# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns
from simplejsonapi import register_action

urlpatterns = patterns('')

@register_action
def echo(**params):
    return params
