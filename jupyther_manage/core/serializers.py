from rest_framework import serializers

from core.models import DockerConainer


class DockerContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockerConainer
