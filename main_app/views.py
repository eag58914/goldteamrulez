from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView
# login imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import matplotlib.pyplot as plt

from .models import Profile, Photo, Activity
from bs4 import BeautifulSoup
import requests

# photo import
import uuid
import boto3

S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com'
BUCKET = 'miloprofilepics'

# Create your views here.


def home(request):
    toReturn = webscrapper()
    return render(request, 'home.html',
                  {
                      'toReturn': toReturn
                  })


def profile(request):
    profile = Profile.objects.get(user_id=request.user.id)
    graphobj = graphs(Profile.objects.get(user_id=request.user.id).activity)
    return render(request, 'profile.html',
                  {
                      'profile': profile,
                      'graphobj' : graphobj
                  }
                  )


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('../profile/create')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


def webscrapper():
    url = "https://www.ideafit.com/fitness-library"
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    grabbedfeed = content.find_all("div", attrs={
                                   "class": "box white article teaser large wide nopad has-image clearfix"})
    toReturn = []
    for x in range(6):
        artical = {
            'img': grabbedfeed[x].img.get("src"),
            'link': url + grabbedfeed[x].h3.a.get('href'),
            'headline': grabbedfeed[x].h3.text,
            'discript': grabbedfeed[x].p.text
        }
        toReturn.append(artical)
    return toReturn


class ProfileCreate(CreateView):
    model = Profile
    fields = ['name', 'dob', 'sport_bio', 'goal']
    success_url = '/profile/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ProfileUpdate(UpdateView):
    model = Profile
    fields = ['name', 'sport_bio', 'goal']
    sucess_url = '/profile/'


class ActivityCreate(CreateView):
    model = Activity
    fields = ['activity', 'weight', 'reps', 'date']
    success_url = '/profile/'


def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)


def add_photo(request, profile_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + \
            photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            photo = Photo(url=url, profile_id=profile_id)
            photo.save()
        except:
            print('An error occurred uploading file to S3')
    return redirect('/profile/')


def graphs(activity):
    run = []
    arms = []
    legs = []
    core = []
    dater = []
    datea = []
    datel = []
    datec = []
    lw = 0
    cw = 0
    aw = 0
    for act in activity:
        if  act.activity = 'r':
            run.append(act.rep)
            dater.append(act.date)
        elif act.activity = 'l':
            legs.append(act.rep)
            datel.append(act.date)
            lw += act.weight
        elif act.activity = 'c':
            core.append(act.rep)
            datec.append(act.date)
            cw += act.weight
        elif act.activity = 'a':
            arms.append(act.rep)
            datea.append(act.date)
            aw += act.weight
    
    plt.plot(dater,run,'ro',datea,arms,'bo',datec,core,'go',datel,legs,'yo')
    plt.ylabel('Reps / Distance')
    plt.xlabel('Date')
    console.log(plt.show());
    return 
        {
        graph :plt.show()
        weights = f"arms:{aw}   legs:{lw}   core:{cw}"
        }