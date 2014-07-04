from django.shortcuts import render
from django.views.generic import View 
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponseForbidden
from django.contrib import auth
from django.contrib.auth.views import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from forms import UserRegistrationForm
from forms import UserLoginForm

from models import CustomUser
from models import Notification

# Using class based views
class UserRegistrationView(View):
    form_class = UserRegistrationForm
    template_name = 'userprofile/registration_template.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')

        return render(request, self.template_name, {'form': form})

class UserRegistrationSuccessView(TemplateView):
    template_name = 'userprofile/successful_registration.html'

    def get_context_data(self, **kwargs):
        context = {}
        return context

class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'userprofile/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            # form.save()
            auth.login(request, form.user_cache)
            return HttpResponseRedirect('/')

        return render(request, self.template_name, {'form': form})

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/')

class UserProfileView(View):
    template_name = 'userprofile/profile.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        me = request.user.customuser
        if 'user_id' in kwargs:
            id_ = kwargs['user_id']
            try:
                user = CustomUser.objects.get(pk=kwargs['user_id'])
            except:
                raise Http404("User does not exist")

        else:
            user = request.user.customuser        
        c = user_context(user, me)
        return render(request, self.template_name, c)
            # {'user_id': user, 'friend': True, 'pics': pics})

class UserDisplayFriends(View):
    template_name = 'userprofile/friend_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        try:
            user = CustomUser.objects.get(pk=user_id)
        except:
            raise Http404

        friend_list = user.friends.filter(friends__id__exact=user.id)
        return render(request, self.template_name, 
            {'list': friend_list, 'user_id': user})

class SearchUsers(View):
    template_name = 'userprofile/search.html'
    results_template = 'userprofile/search_results.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        query = request.POST['q']
        # objects = CustomUser.objects.all()
        results = CustomUser.objects.filter(user__username__contains=query)
        results |= CustomUser.objects.filter(user__first_name__contains=query)
        results |= CustomUser.objects.filter(user__last_name__contains=query)

        return render(request, self.results_template, {'list': results})

class UserAddFriends(View):
    template_name = 'userprofile/profile.html'

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        sender = request.user.customuser
        user = CustomUser.objects.get(pk=user_id)
        if user == sender:
            raise HttpResponseForbidden("Can't add itself.")
        
        user_friends = user.friends.all() 
        sender_notifications = sender.notification.all()
        if sender not in user_friends:            
            # make notification only when adding first
            n = Notification(user=user, source=sender)
            n.save()
        else:
            # delete already generated notification for sender
            m = ""
            for notif in sender_notifications:
                if notif.source == user:
                    m = notif
            if not m == "":
                m.delete()

        sender.friends.add(user)
        sender.save()

        c = user_context(user, sender)
        return render(request, self.template_name, c)
            # {'user_id': user, 'friend': True})

class UserNotifications(View):
    template_name = 'userprofile/notifications.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        user = CustomUser.objects.get(pk=user_id)

        notifications = user.notification.all()
        return render(request, self.template_name, {'list': notifications})

class UserAcceptFriendship(View):
    template_name = 'userprofile/notifications.html'

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        id_ = kwargs['not_id']
        notification = Notification.objects.get(pk=id_)
        user = notification.user
        source = notification.source

        if 'accept' in request.POST:
            # accept friendship
            user.friends.add(source)
        elif 'reject' in request.POST:
            source.friends.remove(user)

        notification.delete()
        notifications = user.notification.all()

        return render(request, self.template_name, {'list': notifications})


def user_context(user, visitor):
    """Get and return dict context for a user profile."""
    friends = False

    if user == visitor or visitor.friends.filter(pk=user.id).exists():
        friends = True

    if friends:
        pics = user.pics.all()
    else:
        pics = user.pics.filter(public=True)

    return {'user_id': user, 'friend': friends, 'pics': pics}
