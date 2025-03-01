# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import re
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Kabupaten(models.Model):
    nama = models.CharField(max_length=100, unique=True)  # Nama Kabupaten/Kota

    def __str__(self):
        return self.nama

class Kecamatan(models.Model):
    kabupaten = models.ForeignKey(Kabupaten, on_delete=models.CASCADE)  # Relasi ke Kabupaten
    nama = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nama}, {self.kabupaten.nama}"

class MasterPerumahan(models.Model):
    nama_perumahan = models.CharField(max_length=255)
    alamat = models.TextField()
    rt = models.IntegerField(null=True, blank=True)  
    rw = models.IntegerField(null=True, blank=True)  
    desa = models.CharField(max_length=100)  # Desa tetap manual
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.SET_NULL, null=True)  # Relasi ke Kecamatan
    kabupaten = models.ForeignKey(Kabupaten, on_delete=models.SET_NULL, null=True)  # Relasi ke Kabupaten
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    alamat_maps = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.nama_perumahan = self.nama_perumahan.upper()  # Konversi ke huruf besar

        # Hapus kata "PERUMAHAN" di awal jika ada
        self.nama_perumahan = re.sub(r'^PERUMAHAN\s+', '', self.nama_perumahan, flags=re.IGNORECASE)

        # Hapus kata "DESA" di awal hanya dari field desa
        self.desa = re.sub(r'^desa\s+', '', self.desa, flags=re.IGNORECASE)

        # Generate Google Maps URL jika koordinat ada
        if self.latitude and self.longitude:
            self.alamat_maps = f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_perumahan

class MasterPenduduk(models.Model):
    perumahan = models.ForeignKey(MasterPerumahan, on_delete=models.CASCADE)
    no_blok = models.IntegerField(null=True, blank=True)
    nama_kk = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('pemilik tetap', 'Pemilik Tetap'),
        ('kosong', 'Kosong'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_kk