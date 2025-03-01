# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import random
import json
from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator

from .models import MasterPerumahan, MasterPenduduk, Kabupaten, Kecamatan
from .forms import MasterPerumahanForm, MasterPendudukForm

@login_required(login_url="/login/")
def index(request):
    # Ambil data jumlah penduduk per perumahan
    data = (
        MasterPenduduk.objects.values('perumahan__nama_perumahan')
        .annotate(jumlah=Count('id'))
        .order_by('-jumlah')
    )

    # Siapkan data untuk Highcharts
    chart_data = {
        "categories": [item['perumahan__nama_perumahan'] for item in data],
        "values": [item['jumlah'] for item in data],
    }

    context = {
        'segment': 'dashboard',
        'perumahan_list': MasterPerumahan.objects.all(),
        'penduduk_list': MasterPenduduk.objects.all(),
        'chart_data': chart_data  # Data dikirim ke template
    }
    return render(request, 'home/dashboard.html', context)

@login_required(login_url="/login/")
def pages(request):
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context = {'segment': load_template.replace('.html', '')}
        return render(request, f'home/{load_template}', context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html')
    except Exception as e:
        print(f"Error: {e}")
        return render(request, 'home/page-500.html')

@login_required
def dashboard_view(request):
    data = (
        MasterPenduduk.objects.values('perumahan__nama_perumahan')
        .annotate(jumlah= Count('id'))
        .order_by('-jumlah')
    )

    # Ubah ke format JSON untuk Highcharts
    chart_data = {
        "categories": [item['perumahan__nama_perumahan'] for item in data],
        "values": [item['jumlah'] for item in data],
    }

    return JsonResponse(chart_data)

@login_required
def transaksi_view(request):
    return render(request, 'home/transaksi.html', {'segment': 'transaksi'})

@login_required
def reporting_view(request):
    return render(request, 'home/reporting.html', {'segment': 'reporting'})

def master_data(request):
    perumahan_filter = request.GET.get('perumahan', '')
    status_filter = request.GET.get('status', '')
    blok_filter = request.GET.get('blok', '')
    kabupaten_filter = request.GET.get('kabupaten', None)
    tab = request.GET.get('tab', 'perumahan')  # Default ke tab 'perumahan'

    # Ambil semua data
    penduduk_list = MasterPenduduk.objects.all()
    perumahan_list = MasterPerumahan.objects.all()

    # Filter berdasarkan perumahan
    if perumahan_filter:
        perumahan_list = perumahan_list.filter(id=perumahan_filter)
        penduduk_list = penduduk_list.filter(perumahan__id=perumahan_filter)

    # Filter berdasarkan status
    if status_filter:
        penduduk_list = penduduk_list.filter(status=status_filter)

    # Filter berdasarkan blok
    if blok_filter:
        penduduk_list = penduduk_list.filter(no_blok=blok_filter)

    # Filter berdasarkan kabupaten dan kecamatan
    if kabupaten_filter:
        perumahan_list = perumahan_list.filter(kabupaten__id=kabupaten_filter)

    # Paginasi Perumahan
    perumahan_paginator = Paginator(perumahan_list, 10)  # 10 data per halaman
    perumahan_page_number = request.GET.get('page')
    perumahan_page = perumahan_paginator.get_page(perumahan_page_number)

    # Paginasi Penduduk
    paginator = Paginator(penduduk_list, 10)
    page_number = request.GET.get('page')
    penduduk_page = paginator.get_page(page_number)
    
    # Get kabupaten dan kecamatan untuk filter dropdown
    kabupaten_options = MasterPerumahan.objects.select_related('kabupaten').distinct()

    context = {
        'segment': 'master',
        'penduduk_page': penduduk_page,
        'perumahan_page': perumahan_page,
        'perumahan_options': MasterPerumahan.objects.all(),
        'status_options': MasterPenduduk.objects.values_list('status', flat=True).distinct(),
        'blok_options': MasterPenduduk.objects.values_list('no_blok', flat=True).distinct(),
        'kabupaten_options': kabupaten_options,
        'active_tab': tab,
        'kabupaten_filter': kabupaten_filter,
    }
    return render(request, 'home/tables_main.html', context)

# CRUD Perumahan
@login_required
def create_perumahan(request):
    form = MasterPerumahanForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        perumahan = form.save(commit=False)

        kabupaten_id = request.POST.get("kabupaten")
        kecamatan_id = request.POST.get("kecamatan")

        if kabupaten_id:
            perumahan.kabupaten = get_object_or_404(Kabupaten, id=kabupaten_id)
        if kecamatan_id:
            perumahan.kecamatan = get_object_or_404(Kecamatan, id=kecamatan_id)

        perumahan.save()
        messages.success(request, "Data Perumahan berhasil ditambahkan.")
        return redirect(f"{reverse('master_data')}?tab=perumahan")

    kecamatan_dict = {}
    for kecamatan in Kecamatan.objects.select_related("kabupaten").all():
        kabupaten_id = str(kecamatan.kabupaten.id)  # Konversi ID ke string agar JSON valid
        if kabupaten_id not in kecamatan_dict:
            kecamatan_dict[kabupaten_id] = []
        kecamatan_dict[kabupaten_id].append({
            "id": kecamatan.id,
            "nama_kecamatan": kecamatan.nama
        })

    context = {
        'form': form,
        'kabupaten_list': Kabupaten.objects.all(),
        'kecamatan_json': json.dumps(kecamatan_dict, ensure_ascii=False),  # Hindari encoding karakter khusus
    }
    return render(request, 'actions/perumahanCreate.html', context)

@login_required
def update_perumahan(request, pk):
    perumahan = get_object_or_404(MasterPerumahan, pk=pk)
    form = MasterPerumahanForm(request.POST or None, instance=perumahan)

    if request.method == "POST" and form.is_valid():
        # Mengambil form yang sudah di-submit
        perumahan = form.save(commit=False)

        # Ambil kabupaten dan kecamatan dari request POST
        kabupaten_id = request.POST.get("kabupaten")
        kecamatan_id = request.POST.get("kecamatan")

        # Set kabupaten dan kecamatan jika ada
        if kabupaten_id:
            perumahan.kabupaten = get_object_or_404(Kabupaten, id=kabupaten_id)
        if kecamatan_id:
            perumahan.kecamatan = get_object_or_404(Kecamatan, id=kecamatan_id)

        # Simpan perubahan data perumahan
        perumahan.save()
        messages.success(request, "Data Perumahan berhasil diperbarui.")
        return redirect(f"{reverse('master_data')}?tab=perumahan")

    # Membuat dictionary kecamatan berdasarkan kabupaten
    kecamatan_dict = {}
    for kecamatan in Kecamatan.objects.select_related("kabupaten").all():
        kabupaten_id = str(kecamatan.kabupaten.id)  # Konversi ID ke string agar JSON valid
        if kabupaten_id not in kecamatan_dict:
            kecamatan_dict[kabupaten_id] = []
        kecamatan_dict[kabupaten_id].append({
            "id": kecamatan.id,
            "nama_kecamatan": kecamatan.nama
        })

    context = {
        'form': form,
        'perumahan': perumahan,
        'kabupaten_list': Kabupaten.objects.all(),
        'kecamatan_json': json.dumps(kecamatan_dict, ensure_ascii=False),  # Hindari encoding karakter khusus
    }
    return render(request, 'actions/perumahanUpdate.html', context)

@login_required
def delete_perumahan(request, pk):
    get_object_or_404(MasterPerumahan, pk=pk).delete()
    messages.success(request, "Data Perumahan berhasil dihapus.")
    return redirect(f"{reverse('master_data')}?tab=perumahan")

# CRUD Penduduk
@login_required
def create_penduduk(request):
    form = MasterPendudukForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        penduduk = form.save(commit=False)
        perumahan_id = request.POST.get("perumahan")
        if perumahan_id:
            penduduk.perumahan = get_object_or_404(MasterPerumahan, id=perumahan_id)
        penduduk.save()
        messages.success(request, "Data Penduduk berhasil ditambahkan.")
        return redirect(f"{reverse('master_data')}?tab=penduduk")  # Redirect ke tab penduduk

    return render(request, 'actions/pendudukCreate.html', {
        'form': form,
        'perumahan_options': MasterPerumahan.objects.all()
    })

@login_required
def update_penduduk(request, pk):
    penduduk = get_object_or_404(MasterPenduduk, pk=pk)
    form = MasterPendudukForm(request.POST or None, instance=penduduk)

    if request.method == "POST" and form.is_valid():
        penduduk = form.save(commit=False)
        perumahan_id = request.POST.get("perumahan")
        if perumahan_id:
            penduduk.perumahan = get_object_or_404(MasterPerumahan, id=perumahan_id)
        penduduk.save()
        messages.success(request, "Data Penduduk berhasil diperbarui.")
        return redirect(f"{reverse('master_data')}?tab=penduduk")

    return render(request, 'actions/pendudukUpdate.html', {
        'form': form,
        'perumahan_options': MasterPerumahan.objects.all(),
        'penduduk': penduduk
    })

@login_required
def delete_penduduk(request, pk):
    get_object_or_404(MasterPenduduk, pk=pk).delete()
    messages.success(request, "Data Penduduk berhasil dihapus.")
    return redirect(f"{reverse('master_data')}?tab=penduduk")

def logout_view(request):
    logout(request)  # Menghapus sesi pengguna
    return redirect('/login/')  # Redirect ke halaman login setelah logout