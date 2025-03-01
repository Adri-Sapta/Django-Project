from django import forms
from .models import MasterPerumahan, MasterPenduduk, Kabupaten, Kecamatan

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
