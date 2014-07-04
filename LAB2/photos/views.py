from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import Http404

from forms import ImageUploadForm
from models import Photo
from models import Comment
# from models import Like

from userprofile.models import CustomUser

@login_required
def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            photo = Photo()
            photo.photo = form.cleaned_data['image']
            photo.public = form.cleaned_data['public']
            photo.name = form.cleaned_data['name']
            photo.owner = user.customuser
            photo.save()
            # print(photo.photo)
            return HttpResponseRedirect('/photos/success_upload/')
    elif request.method == 'GET':
        form = ImageUploadForm()
        return render(request, 'photos/upload.html', {'form': form})
    return render(request, 'photos/upload.html', {'form': form})

def upload_success(request):
    return render(request, 'photos/upload_success.html')

@login_required
def list_images(request):
    return render(request, 'photos/list_images.html', 
        {'user_id': request.user.customuser, 
        'images': request.user.customuser.pics.all()})

@login_required
def show_image(request, image_id):
    try:
        photo = Photo.objects.get(pk=image_id)
    except:
        raise Http404
    # check that user is in friends
    user = request.user.customuser
    if photo.public == False:
        owner = photo.owner
        if user != owner and user not in owner.friends.all():
            return HttpResponseForbidden("Forbidden")

    c = image_context(photo, user)
    return render(request, 'photos/view_image.html', c)
        # {'photo': photo, 'likes': likes, 'liked': liked, 'comments': comments})

@login_required
def like_image(request, image_id):
    try:
        photo = Photo.objects.get(pk=image_id)
    except:
        raise Http404

    user = request.user.customuser
    if photo.public == False:
        owner = photo.owner
        if user != owner and user not in owner.friends.all():
            return HttpResponseForbidden("Forbidden")

    photo.like.add(user)
    photo.save()

    c = image_context(photo, user)
    return render(request, 'photos/view_image.html', c)
        # {'photo': photo, 'likes': likes, 'liked': True, 'comments': comments})

@login_required
def unlike_image(request, image_id):
    try:
        photo = Photo.objects.get(pk=image_id)
    except:
        raise Http404

    user = request.user.customuser
    # likes = photo.like.all()
    photo.like.remove(user)
    photo.save()

    c = image_context(photo, user)
    return render(request, 'photos/view_image.html', c)
        # {'photo': photo, 'likes': likes, 'liked': False, 'comments': comments})

@login_required
def comment(request, image_id):
    try:
        photo = Photo.objects.get(pk=image_id)
    except:
        raise Http404
    if request.method == 'POST':
        # add comment
        text = request.POST['comm']
        user = request.user.customuser
        if photo.public == False:
            owner = photo.owner
            if user != owner and user not in owner.friends.all():
                return HttpResponseForbidden("Forbidden")

        comm = Comment(photo=photo, user=user, text=text)
        comm.save()
        c = image_context(photo, user)
        return render(request, 'photos/view_image.html', c)
            # {'photo': photo, 'likes': likes, 'liked': liked, 'comments': comments})

@login_required
def uncomment(request, image_id, comment_id):
    try:
        photo = Photo.objects.get(pk=image_id)
        comm = Comment.objects.get(pk=comment_id)
    except:
        raise Http404

    if comm.user != request.user.customuser:
        return HttpResponseForbidden("Forbidden")

    comm.delete()
    user = request.user.customuser
    c = image_context(photo, user)

    return render(request, 'photos/view_image.html', c)

@login_required
def tag_image(request, user_id, image_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
        photo = Photo.objects.get(pk=image_id)
    except:
        raise Http404

    accessor = request.user.customuser
    if photo.public == False:
        if accessor != photo.owner and accessor not in photo.owner.friends.all():
            return HttpResponseForbidden("Forbidden")

    if 'list' in request.POST:
        # just fetch a list of friends of the current user
        # print(user)
        friend_list = user.friends.filter(friends__id__exact=user.id)
        # print(friend_list)
        return render(request, 'photos/tag_friends.html', 
            {'user_id': user, 'photo': photo, 'list': friend_list})

    elif 'tag' in request.POST:
        # tag a user on the image
        if accessor not in user.friends.all():
            return HttpResponseForbidden("Forbidden")

        if user not in photo.tag.all():
            # print ("Tagging a user:" + str(user))
            photo.tag.add(user)
            photo.save()
            
    elif 'remove' in request.POST:
        if user in photo.tag.all():
            photo.tag.remove(user)
            photo.save()

    user = request.user.customuser
    c = image_context(photo, user)
    return render(request, 'photos/view_image.html', c)        

@login_required
def privacy(request, image_id):
    try:
        # user = CustomUser.objects.get(pk=user_id)
        photo = Photo.objects.get(pk=image_id)
    except:
        raise Http404  
    
    accessor = request.user.customuser
    if accessor != photo.owner:
        return HttpResponseForbidden("Forbidden")

    if request.method == 'POST':
        if 'publ' in request.POST:
            photo.public = True
            photo.save()
        elif 'priv' in request.POST:
            photo.public = False
            photo.save()

    c = image_context(photo, accessor)  
    return render(request, 'photos/view_image.html', c)

def image_context(photo, user):
    """Returns whole context dict for an image."""
    comments = photo.comments.all()

    likes = photo.like.all()
    liked = False
    if user in likes:
        liked = True

    tags = photo.tag.all()
    tagged = False
    if user in tags:
        tagged = True

    return {'photo': photo, 'likes': likes, 
        'liked': liked, 'comments': comments, 'tags': tags, 'tagged': tagged}