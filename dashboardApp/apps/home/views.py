# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import MasterPerumahan, MasterPenduduk
from .forms import MasterPerumahanForm, MasterPendudukForm

@login_required(login_url="/login/")
def index(request):
    context = {
        'segment': 'index',
        'perumahan_list': MasterPerumahan.objects.all(),
        'penduduk_list': MasterPenduduk.objects.all()
    }
    return render(request, 'home/index.html', context)

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
    return render(request, 'home/index.html', {'segment': 'dashboard'})

@login_required
def transaksi_view(request):
    return render(request, 'home/transaksi.html', {'segment': 'transaksi'})

@login_required
def reporting_view(request):
    return render(request, 'home/reporting.html', {'segment': 'reporting'})

# CRUD Perumahan
@login_required
def perumahan_list(request):
    perumahan = MasterPerumahan.objects.all()
    return render(request, 'home/tables_perumahan.html', {'perumahan_list': perumahan})

@login_required
def create_perumahan(request):
    form = MasterPerumahanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Data Perumahan berhasil ditambahkan.")
        return redirect('index')
    return render(request, 'actions/perumahanCreate.html', {'form': form})

@login_required
def update_perumahan(request, pk):
    perumahan = get_object_or_404(MasterPerumahan, pk=pk)
    form = MasterPerumahanForm(request.POST or None, instance=perumahan)
    if form.is_valid():
        form.save()
        messages.success(request, "Data Perumahan berhasil diperbarui.")
        return redirect('index')
    return render(request, 'actions/perumahanUpdate.html', {'form': form})

@login_required
def delete_perumahan(request, pk):
    get_object_or_404(MasterPerumahan, pk=pk).delete()
    messages.success(request, "Data Perumahan berhasil dihapus.")
    return redirect('index')

# CRUD Penduduk
@login_required
def penduduk_list(request):
    penduduk = MasterPenduduk.objects.all()
    return render(request, 'home/tables_penduduk.html', {'penduduk_list': penduduk})

@login_required
def create_penduduk(request):
    form = MasterPendudukForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Data Penduduk berhasil ditambahkan.")
        return redirect('index')
    return render(request, 'actions/pendudukCreate.html', {'form': form})

@login_required
def update_penduduk(request, pk):
    penduduk = get_object_or_404(MasterPenduduk, pk=pk)
    form = MasterPendudukForm(request.POST or None, instance=penduduk)
    if form.is_valid():
        form.save()
        messages.success(request, "Data Penduduk berhasil diperbarui.")
        return redirect('index')
    return render(request, 'actions/pendudukUpdate.html', {'form': form, 'perumahan_list': MasterPerumahan.objects.all()})

@login_required
def delete_penduduk(request, pk):
    get_object_or_404(MasterPenduduk, pk=pk).delete()
    messages.success(request, "Data Penduduk berhasil dihapus.")
    return redirect('index')
