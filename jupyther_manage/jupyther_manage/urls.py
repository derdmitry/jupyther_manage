from django.conf.urls import url, include
from django.contrib import admin

from core.views import proxy_rewrite

urlpatterns = (
    url(r'^admin/', admin.site.urls),
    url(r'^core/', include('core.urls', namespace='core')),
    url(r'^.*$', proxy_rewrite, name='proxy-rewrite'),


)
