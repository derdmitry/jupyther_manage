from django.conf.urls import url, include
from rest_framework import routers

from views import DockerContainerViewSet, Proxy

router = routers.SimpleRouter()
router.register(r'containers', DockerContainerViewSet)
urlpatterns = (
    url(r'^', include(router.urls)),
    url(r'^proxy/(?P<docker_id>\w+)', Proxy.as_view(), 'proxy-view')

)
