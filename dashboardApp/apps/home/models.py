# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import re
from django.db import models
from django.db.models import Max
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
    
class MasterAnggotaKeluarga(models.Model):
    penduduk = models.ForeignKey(MasterPenduduk, on_delete=models.CASCADE, related_name='anggota_keluarga')
    STATUS_CHOICES = [
        ('ayah', 'Ayah'),
        ('ibu', 'Ibu'),
        ('anak', 'Anak'),
        ('saudara', 'Saudara'),
        ('lainnya', 'Lainnya'),
    ]

    nama = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    tgl_lahir = models.DateField()

    def __str__(self):
        return f"{self.nama} - {self.status}"


class MasterPenyewa(models.Model):
    penduduk = models.ForeignKey(MasterPenduduk, on_delete=models.CASCADE, related_name='penyewa')
    nama_penyewa = models.CharField(max_length=255, null=True, blank=True)
    tgl_mulai_sewa = models.DateField()
    tgl_terakhir_sewa = models.DateField()
    status = models.IntegerField(choices=[(0, "Tidak Aktif"), (1, "Aktif")], default=1)

    def __str__(self):
        return f"{self.penduduk.nama_kk} ({'Aktif' if self.status == 1 else 'Tidak Aktif'})"

class MasterPekerja(models.Model):
    nama_pekerja = models.CharField(max_length=255, null=True, blank=True)
    kode_petugas = models.CharField(max_length=20, unique=True, blank=True)
    STATUS_CHOICES = [
        ('Security', 'Security'),
        ('Petugas Kebersihan', 'Petugas Kebersihan'),
        ('Marbot', 'Marbot'),
    ]
    role = models.CharField(max_length=50, choices=STATUS_CHOICES)
    status = models.IntegerField(choices=[(0, "Tidak Aktif"), (1, "Aktif")], default=1)
    tgl_mulai_bekerja = models.DateField()

    def save(self, *args, **kwargs):
        if not self.kode_petugas:
            last_kode = MasterPekerja.objects.aggregate(Max('kode_petugas'))['kode_petugas__max']
            if last_kode:
                match = re.search(r'PTG-(\d+)', last_kode)
                if match:
                    next_number = int(match.group(1)) + 1
                    self.kode_petugas = f'PTG-{next_number:04d}'
                else:
                    self.kode_petugas = 'PTG-0001'
            else:
                self.kode_petugas = 'PTG-0001'
        super().save(*args, **kwargs)

class MasterPemasukan(models.Model):
    kode = models.CharField(max_length=20, unique=True, blank=True)
    sumber_pemasukan = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=[(0, "Tidak Aktif"), (1, "Aktif")], default=1)

    def save(self, *args, **kwargs):
        if not self.kode:
            last_kode = MasterPemasukan.objects.aggregate(Max('kode'))['kode__max']
            if last_kode:
                match = re.search(r'PMS-(\d+)', last_kode)
                if match:
                    next_number = int(match.group(1)) + 1
                    self.kode = f'PMS-{next_number:04d}'
                else:
                    self.kode = 'PMS-0001'
            else:
                self.kode = 'PMS-0001'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kode} - {self.sumber_pemasukan}"

class Transaksi(models.Model):
    id_warga = models.ForeignKey('MasterPenduduk', on_delete=models.CASCADE)
    tgl_pembayaran = models.DateField(auto_now_add=True)
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.IntegerField(choices=[(0, "Belum Lunas"), (1, "Sudah Lunas")], default=1)
    
    # Pilihan bulan
    BULAN_CHOICES = [
        ('Januari', 'Januari'),
        ('Februari', 'Februari'),
        ('Maret', 'Maret'),
        ('April', 'April'),
        ('Mei', 'Mei'),
        ('Juni', 'Juni'),
        ('Juli', 'Juli'),
        ('Agustus', 'Agustus'),
        ('September', 'September'),
        ('Oktober', 'Oktober'),
        ('November', 'November'),
        ('Desember', 'Desember'),
    ]
    periode_bulan = models.CharField(max_length=20, choices=BULAN_CHOICES)
    
    # Tahun dari 3 tahun lalu hingga sekarang
    periode_tahun = models.IntegerField()

    id_pemasukan = models.ForeignKey('MasterPemasukan', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.id_warga} - {self.periode_bulan} {self.periode_tahun}"
          
