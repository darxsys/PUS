from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='homepage'),

    # login URLs
    url(r'^login/$', views.UserLoginView.as_view(), name='user_login'),
    # TODO: Change to real login succes view
    # url(r'^login/success/$', UserRegistrationSuccessView.as_view(), name='user_login_success'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='user_logout'),
    # TODO: Also change to real logout stuff
    url(r'^logout/success/$', views.UserRegistrationSuccessView.as_view(), name='user_logout'),

    #registration URLs
    url(r'^register/$', views.UserRegistrationView.as_view(), name='user_registration_view'),
    url(r'^register/success/', views.UserRegistrationSuccessView.as_view(), name='user_registration_success'),

    url(r'^user_search/$', views.SearchUsers.as_view(), name='search_users'),
    url(r'^view_profile/$', views.UserProfileView.as_view(), name='view_profile'),
    url(r'^friend_list/(?P<user_id>[0-9]+)/$', views.UserDisplayFriends.as_view(), name='view_profile'),

    # view other users profile
    url(r'^user/(?P<user_id>[0-9]+)/$', 
        views.UserProfileView.as_view(), name='show_user'),
    url(r'^user_add/(?P<user_id>[0-9]+)/$', 
        views.UserAddFriends.as_view(), name='add_user'),
    url(r'^notifications/(?P<user_id>[0-9]+)/$', 
        views.UserNotifications.as_view(), name='show_notifications'),
    url(r'^accept/(?P<not_id>[0-9]+)/$', 
        views.UserAcceptFriendship.as_view(), name='accept_friendship'),
)
