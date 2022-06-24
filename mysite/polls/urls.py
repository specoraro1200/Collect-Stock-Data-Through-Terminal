from django.urls import path
from . import views


urlpatterns = [
            path('index/', views.index,name="ticker"),
            path('index/add/<str:fav>/', views.favoriteAdd,name="favorites"),
            path('index/<str:ticker>/',views.quickLink,name="link"),
            path('frontpage/signup/', views.signup,name="signup"),
            path('frontpage/', views.frontpage,name="frontpage"),
            path('frontpage/login/', views.loginUser,name="login"),
            path('frontpage/favorites/', views.favoriteList,name="list"),
            path('frontpage/logout/', views.logoutUser,name="logout"),
            path('frontpage/insert/', views.insert,name="insert"),
            path('frontpage/about/', views.about,name="about"),
            path('frontpage/advancedsearch/', views.formset_view,name="advanced")
            ]
