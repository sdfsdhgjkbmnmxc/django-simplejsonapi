# -*- coding: utf-8 -*-
from django.db import models


class JsonApiLastResponse(models.Model):
    creation_datetime = models.DateTimeField(auto_now_add=True)
    request_uid = models.CharField(max_length=1024, unique=True)
    jsrequest = models.TextField(blank=True)
    jsresponse = models.TextField(blank=True)

    def __unicode__(self):
        return self.request_uid

    class Meta:
        ordering = ('-creation_datetime',)
