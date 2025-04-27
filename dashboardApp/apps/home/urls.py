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

    path('anggota-keluarga/create/<int:penduduk_id>/', views.create_anggota_keluarga, name='create_anggota_keluarga'),
    path('anggota-keluarga/update/<int:pk>/', views.update_anggota_keluarga, name='update_anggota_keluarga'),
    path('anggota-keluarga/delete/<int:pk>/', views.delete_anggota_keluarga, name='delete_anggota_keluarga'),

    path('penyewa/create/<int:penduduk_id>/', views.create_penyewa, name='create_penyewa'),
    path('penyewa/update/<int:pk>/', views.update_penyewa, name='update_penyewa'),
    path('penyewa/delete/<int:pk>/', views.delete_penyewa, name='delete_penyewa'),

    path('pekerja/create/', views.create_pekerja, name='create_pekerja'),
    path('pekerja/update/<int:pk>/', views.update_pekerja, name='update_pekerja'),
    path('pekerja/delete/<int:pk>/', views.delete_pekerja, name='delete_pekerja'),

    path('pemasukan/create/', views.create_pemasukan, name='create_pemasukan'),
    path('pemasukan/update/<int:pk>/', views.update_pemasukan, name='update_pemasukan'),
    path('pemasukan/delete/<int:pk>/', views.delete_pemasukan, name='delete_pemasukan'),


    path('transaksi/', views.transaksi_view, name='transaksi'),
    path ('transaksi/create', views.transaksi_create, name='transaksi_create'),
    path('transkasi/update/<int:pk>/', views.transaksi_update, name='transaksi_update'),
    path('transkasi/delete/<int:pk>/', views.transaksi_delete, name='transaksi_delete'),

    path('logout/', views.logout_view, name='logout'),
    # Matches any HTML file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
