from django import forms
from datetime import datetime
from .models import MasterPerumahan, MasterPenduduk, Kabupaten, Kecamatan, MasterAnggotaKeluarga, MasterPenyewa, MasterPekerja, MasterPemasukan
from .models import Transaksi

class MasterPerumahanForm(forms.ModelForm):
    kabupaten = forms.ModelChoiceField(
        queryset=Kabupaten.objects.all(), 
        empty_label="Pilih Kabupaten", 
        required=True
    )
    kecamatan = forms.ModelChoiceField(
        queryset=Kecamatan.objects.all(),
        empty_label="Pilih Kecamatan",
        required=True
    )
    class Meta:
        model = MasterPerumahan
        fields = '__all__'

class MasterPendudukForm(forms.ModelForm):
    class Meta:
        model = MasterPenduduk
        fields = '__all__'

class MasterAnggotaKeluargaForm(forms.ModelForm):
    class Meta:
        model = MasterAnggotaKeluarga
        fields = '__all__'

class MasterPenyewaForm(forms.ModelForm):
    class Meta:
        model = MasterPenyewa
        fields = '__all__'

class MasterPekerjaForm(forms.ModelForm):
    class Meta:
        model = MasterPekerja
        exclude = ['kode_petugas']

class MasterPemasukanForm(forms.ModelForm):
    class Meta:
        model = MasterPemasukan
        exclude = ['kode']

class TransaksiForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        exclude = ['created_date', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        current_year = datetime.now().year
        years = [(y, y) for y in range(current_year - 3, current_year + 1)]
        self.fields['periode_tahun'] = forms.ChoiceField(
            choices=years,
            label="Periode Tahun"
        )