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
from datetime import datetime

from .models import MasterPerumahan, MasterPenduduk, Kabupaten, Kecamatan, MasterAnggotaKeluarga, MasterPenyewa, MasterPekerja, MasterPemasukan
from .forms import MasterPerumahanForm, MasterPendudukForm, MasterAnggotaKeluargaForm, MasterPenyewaForm, MasterPekerjaForm, MasterPemasukanForm
from .models import Transaksi
from .forms import TransaksiForm

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
def reporting_view(request):
    return render(request, 'home/reporting.html', {'segment': 'reporting'})

def master_data(request):
    perumahan_filter = request.GET.get('perumahan', '')
    status_filter = request.GET.get('status', '')
    blok_filter = request.GET.get('blok', '')
    kabupaten_filter = request.GET.get('kabupaten', None)
    role_filter = request.GET.get('role', '')
    tab = request.GET.get('tab', 'perumahan')  # Default ke tab 'perumahan'

    # Ambil semua data
    penduduk_list = MasterPenduduk.objects.all()
    perumahan_list = MasterPerumahan.objects.all()
    pekerja_list = MasterPekerja.objects.all()
    pemasukan_list = MasterPemasukan.objects.all()
    anggota_keluarga_list = MasterAnggotaKeluarga.objects.none()
    penyewa_list = MasterPenyewa.objects.none()


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

    #Filter Berdasarkan Role Pekerja
    if role_filter:
        pekerja_list = pekerja_list.filter(role = role_filter)

    # Paginasi Perumahan
    perumahan_paginator = Paginator(perumahan_list.order_by('id'), 10)  # 10 data per halaman
    perumahan_page_number = request.GET.get('page')
    perumahan_page = perumahan_paginator.get_page(perumahan_page_number)

    # Paginasi Penduduk
    paginator = Paginator(penduduk_list.order_by('id'), 10)
    page_number = request.GET.get('page')
    penduduk_page = paginator.get_page(page_number)
    
    # Paginasi Pekerja
    pekerja_paginator = Paginator(pekerja_list.order_by('id'), 10)  # 10 data per halaman
    pekerja_page_number = request.GET.get('page')
    pekerja_page = pekerja_paginator.get_page(pekerja_page_number)

    # Paginasi Pemasukan
    pemasukan_paginator = Paginator(pemasukan_list.order_by('id'), 10) # 10 data per halaman
    pemasukan_page_number = request.GET.get('page')
    pemasukan_page = pemasukan_paginator.get_page(pemasukan_page_number)

    # Jika ada penduduk, ambil data anggota keluarga dan penyewa
    if penduduk_list.exists():
        anggota_keluarga_list = MasterAnggotaKeluarga.objects.select_related('penduduk').filter(penduduk__in=penduduk_list)

        # Paginasi Anggota Keluarga (5 per halaman)
        anggota_keluarga_paginator = Paginator(anggota_keluarga_list.order_by('id'), 5)
        anggota_keluarga_page_number = request.GET.get('anggota_keluarga_page')
        anggota_keluarga_page = anggota_keluarga_paginator.get_page(anggota_keluarga_page_number)

        # Paginasi Penyewa (5 per halaman)
        #penyewa_paginator = Paginator(penyewa_list, 5)
        #penyewa_page_number = request.GET.get('penyewa_page')
        #penyewa_page = penyewa_paginator.get_page(penyewa_page_number)
    
    # Get kabupaten dan kecamatan untuk filter dropdown
    kabupaten_options = MasterPerumahan.objects.select_related('kabupaten').distinct()

    context = {
        'segment': 'master',
        'penduduk_page': penduduk_page,
        'perumahan_page': perumahan_page,
        'pekerja_page' : pekerja_page,
        'pemasukan_page' : pemasukan_page,
        'perumahan_options': MasterPerumahan.objects.all(),
        'status_options': MasterPenduduk.objects.values_list('status', flat=True).distinct(),
        'blok_options': MasterPenduduk.objects.values_list('no_blok', flat=True).distinct(),
        'role_options' : MasterPekerja.objects.values_list('role', flat=True).distinct(),
        'kabupaten_options': kabupaten_options,
        'active_tab': tab,
        'kabupaten_filter': kabupaten_filter,
        'anggota_keluarga_page': anggota_keluarga_page,
        #'penyewa_page': penyewa_page,
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

#CRUD Anggota Keluarga
@login_required
def create_anggota_keluarga(request, penduduk_id):
    penduduk = get_object_or_404(MasterPenduduk, id=penduduk_id)  # Ambil objek Penduduk dari parameter
    form = MasterAnggotaKeluargaForm(request.POST or None)
    print("POST Data:", request.POST)  # Cek data yang dikirim dari form
    print("Form Errors:", form.errors)  # Cek error pada form

    if request.method == "POST" and form.is_valid():
        anggota_keluarga = form.save(commit=False)
        anggota_keluarga.penduduk = penduduk  # Langsung gunakan penduduk dari parameter
        anggota_keluarga.save()
        messages.success(request, "Data Anggota Keluarga berhasil ditambahkan.")
        return redirect(f"{reverse('master_data')}?tab=penduduk")  

    return render(request, 'actions/anggotaKeluargaCreate.html', {
        'form': form,
        'penduduk': penduduk  # Kirimkan penduduk ke template
    })

@login_required
def update_anggota_keluarga(request, pk):
    anggota_keluarga = get_object_or_404(MasterAnggotaKeluarga, pk=pk)
    form = MasterAnggotaKeluargaForm(request.POST or None, instance=anggota_keluarga)

    if request.method == "POST" and form.is_valid():
        anggota_keluarga = form.save(commit=False)
        penduduk_id = request.POST.get("penduduk")
        if penduduk_id:
            anggota_keluarga.penduduk = get_object_or_404(MasterPenduduk, id=penduduk_id)
        anggota_keluarga.save()
        messages.success(request, "Data Anggota Keluarga berhasil diperbarui.")
        penduduk = anggota_keluarga.penduduk  
        return redirect(f"{reverse('master_data')}?tab=penduduk")

    return render(request, 'actions/anggotaKeluargaUpdate.html', {
        'form': form,
        'penduduk_options': MasterPenduduk.objects.all(),
        'anggota_keluarga': anggota_keluarga
    })

@login_required
def delete_anggota_keluarga(request, pk):
    anggota_keluarga = get_object_or_404(MasterAnggotaKeluarga, pk=pk)
    penduduk = anggota_keluarga.penduduk  # Simpan referensi sebelum dihapus

    anggota_keluarga.delete()
    messages.success(request, "Data Anggota Keluarga berhasil dihapus.")

    return redirect(f"{reverse('master_data')}?tab=penduduk")

#Crud Penyewa
@login_required
def create_penyewa(request, penduduk_id):
    penduduk = get_object_or_404(MasterPenduduk, id=penduduk_id)  # Pastikan penduduk valid
    form = MasterPenyewaForm(request.POST or None)
    print("POST Data:", request.POST)  # Cek data yang dikirim dari form
    print("Form Errors:", form.errors)  # Cek error pada form

    if request.method == "POST" and form.is_valid():
        penyewa = form.save(commit=False)
        penyewa.penduduk = penduduk  # Hubungkan langsung ke penduduk yang dipilih
        penyewa.save()
        print(f"Redirecting to: /master/?tab=penyewa&modal_penduduk={penduduk_id}")  # Debugging
        messages.success(request, "Data Penyewa berhasil ditambahkan.")
        return redirect(f"{reverse('master_data')}?tab=penduduk")  # Redirect ke tab penyewa

    return render(request, 'actions/penyewaCreate.html', {
        'form': form,
        'penduduk': penduduk,  # Kirim penduduk yang dipilih
    })

@login_required
def update_penyewa(request, pk):
    penyewa = get_object_or_404(MasterPenyewa, pk=pk)
    form = MasterPenyewaForm(request.POST or None, instance=penyewa)

    if request.method == "POST" and form.is_valid():
        penyewa = form.save(commit=False)
        penduduk_id = request.POST.get("penduduk")
        penyewa.penduduk = get_object_or_404(MasterPenduduk, id=penduduk_id)
        penduduk = penyewa.penduduk
        penyewa.save()
        messages.success(request, "Data Penyewa berhasil diperbarui.")
        return redirect(f"{reverse('master_data')}?tab=penduduk")

    return render(request, 'actions/penyewaUpdate.html', {
        'form': form,
        'penduduk_options': MasterPenduduk.objects.all(),
        'penyewa': penyewa
    })

@login_required
def delete_penyewa(request, pk):
    penyewa = get_object_or_404(MasterPenyewa, pk=pk)  # Ambil data penyewa terlebih dahulu
    penduduk = penyewa.penduduk  # Ambil data penduduk yang terkait (jika ada)
    
    penyewa.delete()  # Hapus penyewa dari database
    messages.success(request, "Data Penyewa berhasil dihapus.")

    # Redirect dengan modal_penduduk jika penduduk tersedia
    return redirect(f"{reverse('master_data')}?tab=penduduk")
@login_required
def create_pekerja(request):
    form = MasterPekerjaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pekerja = form.save()  # kode_petugas otomatis digenerate dari model
        messages.success(request, "Data Pekerja berhasil ditambahkan.")
        return redirect(f"{reverse('master_data')}?tab=pekerja")

    return render(request, 'actions/pekerjaCreate.html', {
        'form': form
    })

@login_required
def update_pekerja(request, pk):
    pekerja = get_object_or_404(MasterPekerja, pk=pk)
    form = MasterPekerjaForm(request.POST or None, instance=pekerja)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Data Pekerja berhasil diperbarui.")
        return redirect(f"{reverse('master_data')}?tab=pekerja")

    return render(request, 'actions/pekerjaUpdate.html', {
        'form': form,
        'pekerja': pekerja
    })

@login_required
def delete_pekerja(request, pk):
    get_object_or_404(MasterPekerja, pk=pk).delete()
    messages.success(request, "Data Pekerja berhasil dihapus.")
    return redirect(f"{reverse('master_data')}?tab=pekerja")

@login_required
def create_pemasukan(request):
    form = MasterPemasukanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pemasukan = form.save()  # kode_pemsukan otomatis digenerate dari model
        messages.success(request, "Data Pemasukan berhasil ditambahkan.")
        return redirect(f"{reverse('master_data')}?tab=pemasukan")

    return render(request, 'actions/pemasukanCreate.html', {
        'form': form
    })

@login_required
def update_pemasukan(request, pk):
    pemasukan = get_object_or_404(MasterPemasukan, pk=pk)
    form = MasterPemasukanForm(request.POST or None, instance=pemasukan)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Data Pemasukan berhasil diperbarui.")
        return redirect(f"{reverse('master_data')}?tab=pemasukan")

    return render(request, 'actions/pemasukanUpdate.html', {
        'form': form,
        'pemasukan': pemasukan
    })

@login_required
def delete_pemasukan(request, pk):
    get_object_or_404(MasterPemasukan, pk=pk).delete()
    messages.success(request, "Data Pemasukan berhasil dihapus.")
    return redirect(f"{reverse('master_data')}?tab=pemasukan")

#Transaksi View
@login_required
def transaksi_view(request):
    transaksi_list = Transaksi.objects.select_related('id_warga', 'id_pemasukan').all().order_by('-created_date')

    # Filter berdasarkan tahun/periode jika ingin
    tahun_filter = request.GET.get('tahun', '')
    bulan_filter = request.GET.get('bulan', '')

    #filter berdasarkan tahun
    if tahun_filter:
        transaksi_list = transaksi_list.filter(periode_tahun=tahun_filter)
    
    # Filter berdasarkan bulan
    if bulan_filter:
        transaksi_list = transaksi_list.filter(periode_bulan=bulan_filter)
    
    bulan_options = Transaksi.BULAN_CHOICES

    paginator = Paginator(transaksi_list, 10)
    page_number = request.GET.get('page')
    transaksi_page = paginator.get_page(page_number)

    context = {
        'segment' : 'transaksi',
        'transaksi_page': transaksi_page,
        'tahun_filter': tahun_filter,
        'tahun_options': range(datetime.now().year - 3, datetime.now().year + 1),
        'bulan_options' : bulan_options

    }
    return render(request, 'home/transaksi_list.html', context)

# Transaksi CRUD
@login_required
def transaksi_create(request):
    form = TransaksiForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transaksi = form.save(commit=False)
        transaksi.created_by = request.user  # ID user login
        transaksi.save()
        return redirect('/transaksi/')  # redirect ke halaman transaksi
    else:
        print("Form errors:", form.errors)  # Tambahkan log ini
    
    bulan_options = [bulan[0] for bulan in Transaksi.BULAN_CHOICES]

    context = {
        'form': form,
        'warga_options': MasterPenduduk.objects.all(),
        'pemasukan_options': MasterPemasukan.objects.all(),
        'bulan_options': bulan_options,
        'tahun_options': range(datetime.now().year - 3, datetime.now().year + 1),
    }

    return render(request, 'actions/transaksiCreate.html', context)

# Transaksi Update
@login_required
def transaksi_update(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    form = TransaksiForm(request.POST or None, instance=transaksi)

    if request.method == "POST" and form.is_valid():
        transaksi = form.save(commit=False)
        transaksi.created_by = request.user  # Update jika perlu
        transaksi.save()
        return redirect('/transaksi/')  # Atau bisa pakai reverse('nama_url')

    else:
        print("Form errors:", form.errors)  # Debug error form jika tidak valid

    bulan_options = [bulan[0] for bulan in Transaksi.BULAN_CHOICES]

    context = {
        'form': form,
        'warga_options': MasterPenduduk.objects.all(),
        'pemasukan_options': MasterPemasukan.objects.all(),
        'bulan_options': bulan_options,
        'tahun_options': range(datetime.now().year - 3, datetime.now().year + 1),
        'transaksi': transaksi,  # Jika perlu ditampilkan di template
    }

    return render(request, 'actions/transaksiUpdate.html', context)


@login_required
def transaksi_delete(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk)
    
    if request.method == "POST":
        transaksi.delete()
        return redirect('/transaksi/')  # atau pakai reverse('transaksi')

    context = {
        'transaksi': transaksi,
    }
    return render(request, 'actions/transaksiDelete.html', context)

def logout_view(request):
    logout(request)  # Menghapus sesi pengguna
    return redirect('/login/')  # Redirect ke halaman login setelah logout