from django.http import HttpResponsePermanentRedirect


class UrlRedirectMiddleware:
    def process_request(self, request):
        host = request.META['HTTP_HOST'] + request.META['PATH_INFO']
        if 'HTTP_REFERER' in request.META:
            if 'proxy' in request.META['HTTP_REFERER'] and not 'rewrite' in request.path:
                redirect_url = request.META['HTTP_REFERER'].replace('proxy', 'rewrite') + 'path' + request.path
                return HttpResponsePermanentRedirect(redirect_url)
