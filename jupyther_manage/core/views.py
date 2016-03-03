from os import path

import docker.tls as tls
from django.conf import settings
from django.shortcuts import get_object_or_404
from docker import Client
from rest_framework import viewsets
from rest_framework.response import Response

from core.models import DockerConainer
from core.serializers import DockerContainerSerializer

tls_config = tls.TLSConfig(
    client_cert=(path.join(settings.CERTS, 'cert.pem'), path.join(settings.CERTS, 'key.pem')),
    ca_cert=path.join(settings.CERTS, 'ca.pem'),
    verify=True
)
client = Client(base_url=settings.DOCKER_URL, tls=tls_config)


class DockerContainerViewSet(viewsets.ModelViewSet):
    queryset = DockerConainer.objects.all()
    serializer_class = DockerContainerSerializer

    def list(self, request):
        queryset = DockerConainer.objects.all()
        serializer = DockerContainerSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = DockerConainer.objects.all()
        container = get_object_or_404(queryset, pk=pk)
        serializer = DockerContainerSerializer(container)
        return Response(serializer.data)

    def create(self, request):
        print request.POST
        serializer = DockerContainerSerializer(request.POST)
        container = serializer.save()

        docker_container = client.create_container(image=container.image)
        container.docker_id = docker_container[u'Id']
        container.save()
        client.start(docker_container)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status='201', headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        docker_id = instance.docker_id
        response = super(DockerContainerViewSet, self).destroy(request, *args, **kwargs)
        docker_container = {u'Id': docker_id}
        client.stop(docker_container)
        client.remove_container(docker_container)
        return response