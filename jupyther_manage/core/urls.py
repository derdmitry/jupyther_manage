from django.conf.urls import url, include
from rest_framework import routers

from views import DockerContainerViewSet, simple_proxy

router = routers.SimpleRouter()
router.register(r'containers', DockerContainerViewSet)
urlpatterns = (
    url(r'^', include(router.urls)),
    url(r'^proxy/(?P<docker_id>\d+)/$', simple_proxy, name='proxy-view'),
)
