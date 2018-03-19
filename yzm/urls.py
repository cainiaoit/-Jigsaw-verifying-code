# -*- coding:utf-8 -*-
from django.conf.urls import url
import views

urlpatterns = [
    #首页
    url(r'^btj/', views.bjt),
    url(r'^pt/', views.pt),
    url(r'^$', views.index),
    url(r'^status/', views.index_post),
    url(r'^demo/', views.demo),
    
    ]


