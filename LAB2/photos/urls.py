from django.conf.urls import patterns, include, url
from django.contrib import admin

import views
from views import upload_pic
from views import upload_success
from views import list_images
# from views import 

urlpatterns = patterns('',
    # photos
    # url(r'^$', include(photos.urls)),
    url(r'^upload_pic/$', upload_pic, name='image_upload'),
    url(r'^success_upload/', upload_success, name='image_upload_ok'),
    url(r'^list_images/$', list_images, name='list_images_own'),
    url(r'^photo/(?P<image_id>[0-9]+)/$', views.show_image, name='show_image'),
    url(r'^like/(?P<image_id>[0-9]+)/$', views.like_image, name='like_image'),
    url(r'^unlike/(?P<image_id>[0-9]+)/$', views.unlike_image, name='unlike_image'),
    url(r'^comment/(?P<image_id>[0-9]+)/$', views.comment, name='comment_image'),
    url(r'^uncomment/(?P<image_id>[0-9]+)/(?P<comment_id>[0-9]+)/$', 
        views.uncomment, name='uncomment_image'),
    url(r'^change_priv/(?P<image_id>[0-9]+)/$', views.privacy, name='comment_image'),

    url(r'^tag/(?P<user_id>[0-9]+)/(?P<image_id>[0-9]+)/$', 
        views.tag_image, name='tag_image'),
    #admin
)