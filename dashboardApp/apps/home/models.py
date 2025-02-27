# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MasterPerumahan(models.Model):
    nama_perumahan = models.CharField(max_length=255)
    alamat = models.TextField()
    rt = models.CharField(max_length=5)
    rw = models.CharField(max_length=5)
    desa = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    kabupaten = models.CharField(max_length=100)
    alamat_maps = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_perumahan

class MasterPenduduk(models.Model):
    perumahan = models.ForeignKey(MasterPerumahan, on_delete=models.CASCADE)
    no_blok = models.CharField(max_length=10)
    nama_kk = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('pemilik tetap', 'Pemilik Tetap'),
        ('kosong', 'Kosong'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_kk