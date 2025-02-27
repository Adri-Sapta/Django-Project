from django import forms
from .models import MasterPerumahan, MasterPenduduk

class MasterPerumahanForm(forms.ModelForm):
    class Meta:
        model = MasterPerumahan
        fields = '__all__'

class MasterPendudukForm(forms.ModelForm):
    class Meta:
        model = MasterPenduduk
        fields = '__all__'
