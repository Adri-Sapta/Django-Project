# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    # Home / Dashboard
    path('', views.index, name='index'),

    #Dashboard
    path('dashboard-data/', views.dashboard_view, name='dashboard_data'),

    # Setting Master
    path('master/', views.master_data, name='master_data'),  # Master Data (Tab)
    path('perumahan/create/', views.create_perumahan, name='create_perumahan'),
    path('perumahan/update/<int:pk>/', views.update_perumahan, name='update_perumahan'),
    path('perumahan/delete/<int:pk>/', views.delete_perumahan, name='delete_perumahan'),

    path('penduduk/create/', views.create_penduduk, name='create_penduduk'),
    path('penduduk/update/<int:pk>/', views.update_penduduk, name='update_penduduk'),
    path('penduduk/delete/<int:pk>/', views.delete_penduduk, name='delete_penduduk'),

    # Transaksi (Placeholder, bisa ditambahkan nanti)
    # path('transaksi/', views.transaksi_view, name='transaksi'),
    path('logout/', views.logout_view, name='logout'),
    # Matches any HTML file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
