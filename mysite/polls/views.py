from curses.ascii import SI
from sre_constants import SUCCESS
from django.db.models import Func
from django.db.models.functions import Round
from django.shortcuts import render
from django.http import  HttpResponseRedirect
import psycopg2
from django.contrib import messages 
from django.shortcuts import redirect
from polls.forms import SignUp, Login, InsertTicker, Search
from polls.models import Data, AuthUser, Favorites
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import subprocess
from django.db.models import F, Q
from django.forms import formset_factory 
from django.db.models import Max
from datetime import date

conn = psycopg2.connect(host="localhost", port="5432", dbname="project", user="sal", password="password")


class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 2)'


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


def convertFrontPageTableLists(a):
    ans = []
    for row in a:
        print(row)
        store = []
        store.append((row[0]))
        store.append((row[1]))
        ans.append(store)
    ans.reverse()
    return ans

def frontpageStartUp():
    cur = conn.cursor()
    cur.execute("select distinct ticker from data order by ticker asc;")
    a = cur.fetchall()
    ans1 = arrayConverter(a)

    cur.execute("select ticker, max(high) from data where date = Current_date group by ticker order by max(high) desc limit 10;")
    query = cur.fetchall()
    ans2 = convertFrontPageTableLists(query)

    cur.execute("select ticker, max(lastprice) from data where date = Current_date group by ticker order by max(lastprice) desc limit 10;")
    query = cur.fetchall()
    ans3 = convertFrontPageTableLists(query)

    cur.execute("select ticker, max(annalyst) from data where date = Current_date group by ticker order by max(annalyst) desc limit 10;")
    query = cur.fetchall()
    ans4 = convertFrontPageTableLists(query)

    cur.execute("select ticker, replace(substr(percentage,2),',','')::DECIMAL as perc from data where date = current_date order by perc desc limit 10;")
    query = cur.fetchall()
    ans5 = convertFrontPageTableLists(query)

    cur.execute("select ticker,max(low) from data where date = current_date group by ticker order by max(low) desc limit 10;")
    query = cur.fetchall()
    ans6 = convertFrontPageTableLists(query)

    cur.execute("select ticker, min(high) from data where date = Current_date group by ticker order by min(high) asc limit 10;")
    query = cur.fetchall()
    ans7 = convertFrontPageTableLists(query)

    cur.execute("select ticker, min(lastprice) from data where date = Current_date group by ticker order by min(lastprice) asc limit 10;")
    query = cur.fetchall()
    ans8 = convertFrontPageTableLists(query)

    cur.execute("select ticker, min(annalyst) from data where date = Current_date group by ticker order by min(annalyst) asc limit 10;")
    query = cur.fetchall()
    ans9 = convertFrontPageTableLists(query)

    cur.execute("select ticker, replace(substr(percentage,2),',','')::DECIMAL as perc from data where date = current_date order by perc asc limit 10;")
    query = cur.fetchall()
    ans10 = convertFrontPageTableLists(query)

    cur.execute("select ticker,min(low) from data where date = current_date group by ticker order by min(low) asc limit 10;")
    query = cur.fetchall()
    ans11 = convertFrontPageTableLists(query)

    return ans1,ans2,ans3,ans4,ans5,ans6,ans7,ans8,ans9,ans10,ans11


def frontpage(request):
    stocks = frontpageStartUp()
    return render(request,"frontpage.html",{"languages":stocks[0],"highEstimate":stocks[1],"highRealprice":stocks[2], \
    "highAnnalyst":stocks[3],"highPercentage":stocks[4],"highLow":stocks[5],"lowEstimate":stocks[6],"lowRealPrice":stocks[7], \
    "lowAnnalyst":stocks[8], "lowPercentage":stocks[9],"lowLow":stocks[10]})


def signup(request):
    form = SignUp(request.POST)
    if request.method == 'POST':
        user_form = SignUp(data=request.POST)
        if(user_form.is_valid()):
            insert = AuthUser(first_name=user_form.cleaned_data['fname'],last_name=user_form.cleaned_data['lname'],email=user_form.cleaned_data['email'],
            username=user_form.cleaned_data['username'],password=make_password(user_form.cleaned_data['password']),is_superuser = False,is_staff=False,is_active= True,date_joined=timezone.now())
            insert.save()
            user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            return redirect('polls:login')
        else:
            return render(request,"signup.html",{"form":form})
    form = SignUp()
    return render(request,"signup.html",{"form":form})


def formset_view(request):
    context ={}
    GeeksFormSet = formset_factory(Search,extra = 1)
    formset = GeeksFormSet(request.POST or None)
    results = False
    if formset.is_valid():
        counter = 0
        Qr = None
        for form in formset:
            if(form.cleaned_data['symbol'] == ' '):
                a = form.cleaned_data['primary']
            else:
                a = form.cleaned_data['primary'] + form.cleaned_data['symbol']
            q = Q(**{"%s" % a:F(form.cleaned_data['secondary'])})
            counter += 1
            if Qr:
                Qr = Qr & q # or & for filtering
            else:
                Qr = q
            formset = GeeksFormSet()

        primary = form.cleaned_data['primary']
        symbol = form.cleaned_data['symbol']
        secondary = form.cleaned_data['secondary']
        # today = form.cleaned_data['today']
        # if(today == True):
        #     Qr = Qr & Q(date = date.today())
        if(symbol == '__lt'):
            results = Data.objects.filter(Qr).values('ticker').annotate(Max('date'),Max('lastprice'),Max('median'),Max('low'),Max('high'),store=Round((Max(F(secondary))-Max(F(primary))))).order_by('ticker')        
        elif(symbol == '__gt'):
            results = Data.objects.filter(Qr).values('ticker').annotate(Max('date'),Max('lastprice'),Max('median'),Max('low'),Max('high'),store=Round((Max(F(primary))-Max(F(secondary))))).order_by('ticker')
        elif(symbol == ' '):
            results = Data.objects.filter(Qr).values('ticker').annotate(Max('date'),Max('lastprice'),Max('median'),Max('low'),Max('high'),store=Round((Max(F(primary))-Max(F(secondary))))).order_by('ticker')
        print(results.query)
        if results:
            return render(request, "advancedsearchGraph.html",{"results":results})
        elif(results is not False and len(results) == 0):
            messages.error(request, "Search returned zero results")
        
    context['formset']= formset
    return render(request, "advancedsearch.html", context)


def loginUser(request): 
    form = Login(request.POST)
    if request.method == 'POST':
        user_form = Login(data = request.POST)
        if(user_form.is_valid()):
            user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            login(request,user)
            return redirect('polls:frontpage')
        else:
            return render(request,"login.html",{"form":form})
    form = Login()
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


@login_required(login_url='polls:signup')
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
    rating = store[9]

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
    return render(request,"stock.html",{"stock" : stock,"barChart" : barChart,"lineGraph":lineGraph,"filter":filter,"list":dictionary,"rating":rating})


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
            messages.warning(request, "This ticker is already added. Please add another ticker")
            return render(request,"insertTicker.html",{"form":form})
        else:
            store = subprocess.run(["bash", "/mnt/c/Users/scpec/mysite/polls/check.sh",stock])  
            if(store.returncode is 0):
                messages.success(request, "This ticker has been added and CNN Stock Predictor will now keep track of this ticker")
                file_object = open('/mnt/c/Users/scpec/mysite/list.csv', 'a')
                file_object.write(stock +'\n')
                file_object.close()
                return render(request,"insertTicker.html",{"form":form})
            else:
                messages.error(request, "An error occured while adding this ticker. Ensure this ticker is covered by CNN and try again")
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
    rating = store[9]
    
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

    return render(request,"stock.html",{"stock" : ticker,"barChart" : barChart,"lineGraph":lineGraph,"filter":filter,"list":dictionary,"rating":rating})