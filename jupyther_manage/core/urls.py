from django.conf.urls import url, include
from rest_framework import routers

from views import DockerContainerViewSet

router = routers.SimpleRouter()
router.register(r'containers', DockerContainerViewSet)
urlpatterns = (
    url(r'^', include(router.urls)),
)
