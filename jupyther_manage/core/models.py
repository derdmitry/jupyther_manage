from __future__ import unicode_literals

import random

from django.conf import settings
from django.db import models


# Create your models here.

def rand_port():
    r = None
    exclude = [x[0] for x in (DockerConainer.objects.all().values_list('port'))]
    while r in exclude or r is None:
        r = random.randrange(2000, 65535)
    return r


class DockerConainer(models.Model):
    docker_id = models.CharField(max_length=64, blank=True)
    docker_user = models.CharField(max_length=64)
    image = models.CharField(max_length=255, default=settings.DEFAULT_IMAGE)
    address = models.CharField(max_length=255, blank=True)
    port = models.IntegerField(unique=True, default=rand_port)
    is_active = models.BooleanField(default=True)
