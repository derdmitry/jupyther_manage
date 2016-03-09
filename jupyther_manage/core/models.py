from __future__ import unicode_literals

from django.conf import settings
from django.db import models


# Create your models here.


class DockerConainer(models.Model):
    docker_id = models.CharField(max_length=64, blank=True)
    docker_user = models.CharField(max_length=64)
    image = models.CharField(max_length=255, default=settings.DEFAULT_IMAGE)
    address = models.CharField(max_length=255, blank=True)
    port = models.IntegerField(default=8000)
    is_active = models.BooleanField(default=True)
