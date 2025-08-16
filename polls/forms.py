from django import forms
from .models import Server, Paket, IPPool, Client


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
        fields = ['name', 'price', 'limit', 'id_ip_pool']
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Paket'}),
        'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 200000'}),
        'limit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 2M/2M'}),
        'id_ip_pool': forms.Select(attrs={'class': 'form-control'}),
    }
    def clean_limit(self):
        limit = self.cleaned_data.get('limit')
        if limit:
            return limit.upper()
        return limit
    
class ipPoolForm(forms.ModelForm):
    class Meta : 
        model = IPPool
        fields = ['name', 'ip_range', 'id_server']
        widgets = {
        'id_server': forms.Select(attrs={'class': 'form-control'}),
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Ip pool'}),
        'ip_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 192.168.0.1 - 192.168.0.255'}),
    }
        
   
        

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['id_paket', 'name', 'address', 'phone', 'pppoe', 'password', 'lat', 'long']
        widgets = {
            'id_paket': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Pelanggan'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Alamat Pelanggan'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan No Hp Pelanggan'}),
            'pppoe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan id pppoe Pelanggan'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan password id pppoe Pelanggan'}),
            'lat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan latitude lokasi'}),
            'long': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan longitude lokasi'}),
            
        }
    def clean_pppoe(self):
        pppoe = self.cleaned_data.get('pppoe')

        # 1. Tidak boleh ada spasi
        if ' ' in pppoe:
            raise forms.ValidationError("ID PPPoE tidak boleh mengandung spasi.")

        # 2. Harus unik, kecuali untuk data yang sedang diedit
        qs = Client.objects.filter(pppoe=pppoe)
        if self.instance.pk:  # Jika sedang edit, jangan cek dirinya sendiri
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("ID PPPoE ini sudah digunakan, silakan pilih yang lain.")

        return pppoe

