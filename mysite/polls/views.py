from curses.ascii import SI
from urllib.request import Request
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
import psycopg2
import json
from collections import OrderedDict
from polls.forms import SignUp, Login
from django.contrib.auth.models import User
from polls.models import Data, AuthUser, Favorites
from datetime import date
import datetime
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

conn = psycopg2.connect(host="localhost", port="5432", dbname="project", user="sal", password="password")

def arrayConverter(dict):
    ans1 = []
    for row in dict:
        ans1.append((row[0]))
    return ans1


def frontpageStartUp():
    cur = conn.cursor()
    cur.execute("select distinct ticker from data order by ticker asc;")
    a = cur.fetchall()
    ans1 = arrayConverter(a)

    cur.execute("select distinct ticker from data where high = (select max(high) from data);")
    a = cur.fetchall()
    ans2 = arrayConverter(a)
    return ans1,ans2


def frontpage(request):
    stocks = frontpageStartUp()
    return render(request,"frontpage.html",{"languages":stocks[0],"large":stocks[1][0]})


def signup(request):
    form = SignUp(request.POST)
    if request.method == 'POST':
        user_form = SignUp(data=request.POST)
        if(user_form.is_valid()):
            insert = AuthUser(first_name=user_form.cleaned_data['fname'],last_name=user_form.cleaned_data['lname'],email=user_form.cleaned_data['email'],
            username=user_form.cleaned_data['username'],password=make_password(user_form.cleaned_data['password']),is_superuser = False,is_staff=False,is_active= True,date_joined=timezone.now())
            insert.save()
            user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            login(request, user)
            stocks = frontpageStartUp()
            return render(request,"frontpage.html",{"languages":stocks[0],"large":stocks[1][0]})
        else:
            return render(request,"signup.html",{"form":form})
    form = SignUp()
    return render(request,"signup.html",{"form":form})


def loginUser(request): 
    form = Login()
    if request.method == 'POST':
        user_form = Login(data = request.POST)
        if(user_form.is_valid()):
            user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            login(request,user)
            stocks = frontpageStartUp()
            return render(request,"frontpage.html",{"languages":stocks[0],"large":stocks[1][0]})
        else:
            return render(request,"login.html",{"form":form})
    return render(request,"login.html",{"form":form})


def logoutUser(request):
    logout(request)
    return frontpage(request)


# def index(request,name):
#     cur = conn.cursor()

#     stock = None
#     if request.method == 'POST':
#         stock = request.POST['searchbar'].upper()
#     cur.execute("select * from data where ticker like %s order by date desc", [name])
#     print(name,44)
#     store = cur.fetchone()
#     barChart = []
#     barChart.append(store[2])
#     barChart.append(store[3])
#     barChart.append(store[4])
#     cur.execute("select * from data where ticker like %s order by date desc", [name])
#     store = cur.fetchall()
#     lineGraph = [[],[],[],[]]

#     for day in store:
#         lineGraph[0].append(day[2])
#         lineGraph[1].append(day[3])
#         lineGraph[2].append(day[4])
#         lineGraph[3].append(day[8].strftime("%m/%d/%Y"))

#     lineGraph[3].reverse()
#     return render(request,"stock.html",{"stock" : name,"barChart" : barChart,"lineGraph":lineGraph})


@login_required
def favoriteAdd(request,fav):
    a = AuthUser(id = request.user.id)    
    filter = Favorites.objects.filter(ticker = fav, currentuser = request.user.id)
    if(filter):
        filter.delete()
    else:
        here = Favorites(ticker = fav,currentuser = a)
        here.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def favoriteList(request):
    list = Favorites.objects.filter(currentuser = request.user.id)
    fixedList = []
    for row in list:
        store = []
        store.append(row.ticker)
        store.append(row.currentuser.id)
        fixedList.append(store)
    print(fixedList)
    return render(request,"favorites.html",{"list":fixedList})


def index(request):
    cur = conn.cursor()
    stock = None
    if request.method == 'GET':
        stock = request.GET['searchbar'].upper()

    filter = Favorites.objects.filter(ticker = request.GET['searchbar'].upper(), currentuser = request.user.id)
    cur.execute("select * from data where ticker like %s order by date desc", [stock])
    store = cur.fetchone()
    barChart = []
    barChart.append(store[2])
    barChart.append(store[3])
    barChart.append(store[4])
    cur.execute("select * from data where ticker like %s order by date desc", [stock])
    store = cur.fetchall()
    lineGraph = [[],[],[],[]]

    for day in store:
        lineGraph[0].append(day[2])
        lineGraph[1].append(day[3])
        lineGraph[2].append(day[6])
        lineGraph[3].append(day[8].strftime("%m/%d/%Y"))

    lineGraph[3].reverse()
    lineGraph[2].reverse()
    lineGraph[1].reverse()
    lineGraph[0].reverse()

    return render(request,"stock.html",{"stock" : stock,"barChart" : barChart,"lineGraph":lineGraph,"filter":filter})