from curses.ascii import SI
from sre_constants import SUCCESS
from urllib.request import Request
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
import psycopg2
from django.contrib import messages #import messages
from django.shortcuts import redirect
from collections import OrderedDict
from polls.forms import SignUp, Login, InsertTicker
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
import subprocess
conn = psycopg2.connect(host="localhost", port="5432", dbname="project", user="sal", password="password")

def arrayConverter(dict):
    ans1 = []
    for row in dict:
        ans1.append((row[0]))
    return ans1


def extractBasicStockData(stock):
    cur = conn.cursor()
    cur.execute("select * from data where ticker like %s order by date desc", [stock])
    store = cur.fetchone()
    barChart = []
    barChart.append(store[2])
    barChart.append(store[3])
    barChart.append(store[4])
    return barChart


def frontpageStartUp():
    cur = conn.cursor()
    cur.execute("select distinct ticker from data order by ticker asc;")
    a = cur.fetchall()
    ans1 = arrayConverter(a)

    cur.execute("select distinct ticker from data where high = (select max(high) from data);")
    a = cur.fetchall()
    ans2 = arrayConverter(a)

    cur.execute("select ticker, max(high) from data group by ticker order by max(high) desc limit 10;")
    a = cur.fetchall()
    ans3 = []
    for row in a:
        store = []
        store.append((row[0]))
        store.append((row[1]))
        ans3.append(store)

    cur.execute("select ticker, max(lastprice) from data group by ticker order by max(lastprice) desc limit 10;")
    a = cur.fetchall()
    ans4 = []
    for row in a:
        store = []
        store.append((row[0]))
        store.append((row[1]))
        ans4.append(store)
    ans3.reverse()
    ans4.reverse()
    return ans1,ans2,ans3,ans4


def frontpage(request):
    stocks = frontpageStartUp()

    return render(request,"frontpage.html",{"languages":stocks[0],"large":stocks[1][0],"tableData":stocks[2],"realPrice":stocks[3]})


def signup(request):
    form = SignUp(request.POST)
    if request.method == 'POST':
        user_form = SignUp(data=request.POST)
        if(user_form.is_valid()):
            insert = AuthUser(first_name=user_form.cleaned_data['fname'],last_name=user_form.cleaned_data['lname'],email=user_form.cleaned_data['email'],
            username=user_form.cleaned_data['username'],password=make_password(user_form.cleaned_data['password']),is_superuser = False,is_staff=False,is_active= True,date_joined=timezone.now())
            insert.save()
            user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            # login(request, user)
            # stocks = frontpageStartUp()
            #return render(request,"login.html")
            return redirect('polls:login')
            #return render(request,"frontpage.html",{"languages":stocks[0],"large":stocks[1][0]})
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
            return redirect('polls:frontpage')
            #return render(request,"frontpage.html",{"languages":stocks[0],"large":stocks[1][0]})
        else:
            return render(request,"login.html",{"form":form})
    return render(request,"login.html",{"form":form})


def logoutUser(request):
    logout(request)
    return redirect('polls:frontpage')


@login_required(login_url='polls:signup')
def favoriteAdd(request,fav):
    a = AuthUser(id = request.user.id)    
    filter = Favorites.objects.filter(ticker = fav, currentuser = request.user.id)
    if(filter):
        filter.delete()
        messages.success(request, "Removed " + fav + " from favorites list.")
    else:
        here = Favorites(ticker = fav,currentuser = a)
        here.save()
        messages.success(request, "Added " + fav + " into your favorites list.")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def favoriteList(request):
    cur = conn.cursor()
    list = Favorites.objects.filter(currentuser = request.user.id)
    fixedFavoriteList = []
    for row in list:
        fixedStock = []
        cur.execute("select * from data where ticker like %s order by date desc", [row.ticker])
        stockData = cur.fetchone()
        fixedStock.append(row.ticker)
        fixedStock.append(stockData[2])
        fixedStock.append(stockData[3])
        fixedStock.append(stockData[4])
        fixedStock.append(stockData[6])
        fixedFavoriteList.append(fixedStock)
    return render(request,"favorites.html",{"list":fixedFavoriteList})


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
    lineGraph = [[],[],[],[],[]]
    for day in store:
        lineGraph[0].append(day[2])
        lineGraph[1].append(day[3])
        lineGraph[2].append(day[4])
        lineGraph[3].append(day[6])
        lineGraph[4].append(day[8].strftime("%m/%d/%Y"))
    lineGraph[4].reverse()
    lineGraph[3].reverse()
    lineGraph[2].reverse()
    lineGraph[1].reverse()
    lineGraph[0].reverse()
    for x in range(0,len(lineGraph[0])):
        lineGraph[0][x] = float(lineGraph[0][x])
    for x in range(0,len(lineGraph[1])):
        lineGraph[1][x] = float(lineGraph[1][x])    
    for x in range(0,len(lineGraph[2])):
        lineGraph[2][x] = float(lineGraph[2][x])
    for x in range(0,len(lineGraph[3])):
        lineGraph[3][x] = float(lineGraph[3][x])
    dictionary = {"lesser":0,"middle":0,"greater":0}
    for x in range(0,len(lineGraph[0])):
        if lineGraph[3][x] <= lineGraph[1][x]:
            dictionary['lesser'] = dictionary.get('lesser') + 1 
        elif lineGraph[3][x]>= lineGraph[0][x]:
            dictionary['greater'] =  dictionary.get('greater')+1
        else:
            dictionary['middle'] =  dictionary.get('middle')+1
    return render(request,"stock.html",{"stock" : stock,"barChart" : barChart,"lineGraph":lineGraph,"filter":filter,"list":dictionary})

def insert(request):
    form = InsertTicker()
    if request.method == 'GET':
        cur = conn.cursor()
        cur.execute("select distinct ticker from data order by ticker asc;")
        a = cur.fetchall()
        ans1 = arrayConverter(a)
        stock = request.GET.get('search')
        if stock is None:
            return render(request,"insertTicker.html",{"form":form})
        stock = stock.upper()
        if stock in ans1:
            messages.success(request, "This ticker is already added. Please add another ticker")
            return render(request,"insertTicker.html",{"form":form})
        else:
            store = subprocess.run(["bash", "/mnt/c/Users/scpec/mysite/polls/check.sh",stock])  
            if(store.returncode is 0):
                messages.success(request, "This ticker has been added and CNN Stock Predictor will now keep track of this ticker")
                file_object = open('/mnt/c/Users/scpec/Downloads/list.csv', 'a')
                file_object.write(stock +'\n')
                file_object.close()
                return render(request,"insertTicker.html",{"form":form})
            else:
                messages.success(request, "An error occured while adding this ticker. Ensure this ticker is covered by CNN and try again")
                return render(request,"insertTicker.html",{"form":form})

    return render(request,"insertTicker.html",{"form":form})

def about(request):
    
    return render(request, 'about.html')    

def quickLink(request,ticker):
    cur = conn.cursor()
    filter = Favorites.objects.filter(ticker = ticker, currentuser = request.user.id)  
    cur.execute("select * from data where ticker like %s order by date desc", [ticker])
    store = cur.fetchone()
    barChart = []
    barChart.append(store[2])
    barChart.append(store[3])
    barChart.append(store[4])
    cur.execute("select * from data where ticker like %s order by date desc", [ticker])
    store = cur.fetchall()
    lineGraph = [[],[],[],[],[]]
    for day in store:
        lineGraph[0].append(day[2])
        lineGraph[1].append(day[3])
        lineGraph[2].append(day[4])
        lineGraph[3].append(day[6])
        lineGraph[4].append(day[8].strftime("%m/%d/%Y"))
    lineGraph[4].reverse()
    lineGraph[3].reverse()
    lineGraph[2].reverse()
    lineGraph[1].reverse()
    lineGraph[0].reverse()
    for x in range(0,len(lineGraph[0])):
        lineGraph[0][x] = float(lineGraph[0][x])
    for x in range(0,len(lineGraph[1])):
        lineGraph[1][x] = float(lineGraph[1][x])    
    for x in range(0,len(lineGraph[2])):
        lineGraph[2][x] = float(lineGraph[2][x])
    for x in range(0,len(lineGraph[3])):
        lineGraph[3][x] = float(lineGraph[3][x])
    dictionary = {"lesser":0,"middle":0,"greater":0}
    for x in range(0,len(lineGraph[0])):
        if lineGraph[3][x] <= lineGraph[1][x]:
            dictionary['lesser'] = dictionary.get('lesser') + 1 
        elif lineGraph[3][x]>= lineGraph[0][x]:
            dictionary['greater'] =  dictionary.get('greater')+1
        else:
            dictionary['middle'] =  dictionary.get('middle')+1

    return render(request,"stock.html",{"stock" : ticker,"barChart" : barChart,"lineGraph":lineGraph,"filter":filter,"list":dictionary})