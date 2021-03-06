from django.http import HttpResponse
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count
from .models import Video
from .forms import VideoForm, UserForm, LoginForm
import requests
from django.conf import settings


def video_list(request):
    video_list = Video.objects.select_related('author').prefetch_related('likes_user').all()
   
    search_key = request.GET.get('search_key') # 검색어 가져오기
    if search_key: # 만약 검색어가 존재하면
        video_list = video_list.filter(title__icontains=search_key) # 해당 검색어를 포함한 queryset 가져오

    return render(request, 'video/video_list.html', {'video_list':video_list, 'Category':Video.Category})

def video_category(request, category):
    # order by sum of likes_user by descending
    video_list = Video.objects.select_related('author').prefetch_related('likes_user').filter(category=category).annotate(num_likes=Count('likes_user')).order_by('-num_likes')
    return render(request, 'video/video_category.html', {'video_list':video_list, 'Category':Video.Category, 'category':category})

@login_required
def video_new(request):
    if request.method == 'POST': # 새로운 비디오 데이터를 업로드할 때
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save(commit=False) # 받은 데이터를 바로 Video모델에 저장하지 말기
            video.author = request.user # author 추가
            video.save() # 변경사항 저장
            return redirect('video_list')
        else:
            return HttpResponse(form.errors.values())
    elif request.method == 'GET': # 새로운 비디오를 추가할 템플릿을 가져와야할 때
        return render(request, 'video/video_new.html', {'Category':Video.Category})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    videosinfo = get_object_or_404(Video, pk=pk)
    captionsinfo =  get_object_or_404(Video, pk=pk)

    video_url ='https://www.googleapis.com/youtube/v3/videos'
    captions_url='https://www.googleapis.com/youtube/v3/captions'
    channelId_url='https://www.googleapis.com/youtube/v3/channels'
    params = {
        'part' : 'snippet',
        'id' : video.video_key,
        'key' : settings.YOUTUBE_DATA_API_KEY
    }
    params2 = {
        'part' : 'snippet',
        'videoId' : video.video_key,
        'key' : settings.YOUTUBE_DATA_API_KEY
    }



    r=requests.get(video_url, params=params)
    rc=requests.get(captions_url, params=params2)

    
    results=(r.json()['items'])
    results2=(rc.json()['items'])


    videosinfo=[]
    captionsinfo=[]
    channelsinfo=[]
    for result in results:
        video_data={
            'title' : result['snippet']['title'],
            'publishedAt': result['snippet']['publishedAt'],
            'channelTitle' : result['snippet']['channelTitle'],
            'defaultAudioLanguage' : result['snippet']['defaultAudioLanguage'],
        }
        channelId=result['snippet']['channelId']

        videosinfo.append(video_data)


    for result2 in results2:
        caption_data={
            'language' : result2['snippet']['language']
        }

        captionsinfo.append(caption_data)
    
    paramschannel={
        'part' : 'snippet',
        'id' : channelId,
        'key' : settings.YOUTUBE_DATA_API_KEY
    }

    rch=requests.get(channelId_url, params=paramschannel)
    resultsch=(rch.json()['items'])
    for resultch in resultsch:
        channel_data={
        'country': resultch['snippet']['country']
        }    
        channelsinfo.append(channel_data)







    context = {
        'videosinfo' : videosinfo,
        'video': video,
        'captionsinfo' : captionsinfo,
        'channelsinfo': channelsinfo,
    }

    return render(request, 'video/video_detail.html', context)


@login_required
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)

    # if user is not the author of video, permission denied
    if video.author!=request.user:
        return HttpResponse('Delete failed. Permission denied.')

    video.delete()
    return redirect('video_list')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            return redirect('video_list')
    else:
        form = UserForm()
        return render(request, 'video/user_new.html')
        
def signin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect('video_list')
        return HttpResponse('Login failed. Try again.')
    else:
        form = LoginForm()
        return render(request, 'video/user_login.html')

def signout(request):
    logout(request)
    return redirect('video_list')

@login_required
@require_POST
def video_like(request):
    pk = request.POST.get('pk', None)
    video = get_object_or_404(Video, pk=pk)
    user = request.user

    if video.likes_user.filter(id=user.id).exists():
        video.likes_user.remove(user)
        message = '좋아요 취소'
    else:
        video.likes_user.add(user)
        message = '좋아요'

    context = {'likes_count':video.count_likes_user(), 'message': message}
    return HttpResponse(json.dumps(context), content_type="application/json")

@login_required
def my_video(request):
    user = request.user
    myVideo = Video.objects.filter(author=user)
    return render(request, 'video/my_video.html', {'myVideo':myVideo})

@login_required
def like_video(request):
    user = request.user
    likesVideo = Video.objects.filter(likes_user=user)
    return render(request, 'video/like_video.html', {'likesVideo':likesVideo})