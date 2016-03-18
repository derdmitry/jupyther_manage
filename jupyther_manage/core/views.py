import re
import urllib

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from docker import Client
from rest_framework import viewsets
from rest_framework.response import Response

from core.models import DockerConainer
from core.serializers import DockerContainerSerializer

REWRITE_RE = re.compile(r'((?:src|action|href)=["\'])/(?!\/)')


client = Client()


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
        serializer = DockerContainerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        container = serializer.save()
        docker_container = client.create_container(image=container.image)
        container.docker_id = docker_container[u'Id']
        container.save()
        port = {8888: container.port}
        client.start(docker_container, port_bindings=port)
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


class Proxy(View):
    base_url = '172.17.0.2:8888'
    rewrite = False

    def dispatch(self, request, *args, **kwargs):
        self.url = request.path.replace(self.base_url, '')
        self.original_request_path = request.path
        request = self.normalize_request(request)

        response = super(Proxy, self).dispatch(request, *args, **kwargs)

        if self.rewrite:
            response = self.rewrite_response(request, response)
        return response

    def normalize_request(self, request):
        if not self.url.startswith('/'):
            self.url = '/' + self.url
        request.path = self.url
        request.path_info = self.url
        request.META['PATH_INFO'] = self.url
        return request

    def rewrite_response(self, request, response):

        proxy_root = self.original_request_path.rsplit(request.path, 1)[0]
        response.content = REWRITE_RE.sub(r'\1{}/'.format(proxy_root),
                                          response.content)
        return response

    def get(self, *args, **kwargs):
        return self.get_response()

    def post(self, request, *args, **kwargs):
        headers = {}
        if request.META.get('CONTENT_TYPE'):
            headers['Content-type'] = request.META.get('CONTENT_TYPE')
        return self.get_response(body=request.body, headers=headers)

    def get_full_url(self, url):

        param_str = self.request.GET.urlencode()
        request_url = u'%s%s' % (self.base_url, url)
        request_url += '?%s' % param_str if param_str else ''
        return request_url

    def create_request(self, url, body=None, headers={}):
        request = urllib.request.Request(url, body, headers)
        return request

    def get_response(self, body=None, headers={}):
        request_url = self.get_full_url(self.url)
        request = self.create_request(request_url, body=body, headers=headers)
        response = urllib.request.urlopen(request)
        try:
            response_body = response.read()
            status = response.getcode()
        except urllib.error.HTTPError as e:
            response_body = e.read()
            status = e.code
        return HttpResponse(response_body, status=status,
                            content_type=response.headers['content-type'])


def proxy_rewrite(request, docker_id, proxy_path):
    container = DockerConainer.objects.get(id=docker_id)
    if proxy_path:
        proxy_url = 'http://127.0.0.1:%s/%s' % (container.port, proxy_path)
    else:
        proxy_url = 'http://127.0.0.1:%s/' % container.port
    response = urllib.urlopen(proxy_url)
    response_body = response.read()
    status = response.getcode()
    return HttpResponse(response_body, status=status,
                        content_type=response.headers['content-type'])

    return HttpResponse('not ok')


def simple_proxy(request, docker_id, proxy_path=None):
    container = DockerConainer.objects.get(id=docker_id)
    path = request.path.replace(reverse('core:proxy-view', kwargs={'docker_id': docker_id}), '')
    if proxy_path:
        proxy_url = 'http://127.0.0.1:%s/%s' % (container.port, proxy_path)
    else:
        proxy_url = 'http://127.0.0.1:%s/' % container.port
    response = urllib.urlopen(proxy_url)
    response_body = response.read()
    status = response.getcode()
    return HttpResponse(response_body, status=status,
                            content_type=response.headers['content-type'])
