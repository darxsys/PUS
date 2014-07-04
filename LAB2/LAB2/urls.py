from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # home
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='homepage'),
    # users
    url(r'^users/', include('userprofile.urls')),

    # photos
    url(r'^photos/', include('photos.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                 {'document_root': settings.MEDIA_ROOT}),
    #admin
    url(r'^admin/', include(admin.site.urls)),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

