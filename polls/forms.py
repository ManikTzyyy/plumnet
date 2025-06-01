from django import forms
from .models import Server, Paket, IPPool


#server
class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'host', 'username', 'password', 'genieacs']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Server'}),
            'host': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Host IP'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Password'}),
            'genieacs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan IP GenieACS, Kosongkan Jika tidak ada'}),
        }

class PaketForm(forms.ModelForm):
    class Meta : 
        model = Paket
        fields = ['name', 'price', 'limit', 'ip_pool']
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Paket'}),
        'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 200000'}),
        'limit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 2M/2M'}),
        'ip_pool': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Pilih IP range'}),
    }
    def clean_limit(self):
        limit = self.cleaned_data.get('limit')
        if limit:
            return limit.upper()
        return limit
    
class ipPoolForm(forms.ModelForm):
    class Meta : 
        model = IPPool
        fields = ['name', 'ip_range']
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Ip pool'}),
        'ip_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 192.168.0.1 - 192.168.0.255'}),
    }

