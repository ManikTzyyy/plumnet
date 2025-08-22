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

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        ip_pool = cleaned_data.get('id_ip_pool')

        if not name or not ip_pool:
            return cleaned_data

        if " " in name:
            self.add_error('name', "Nama Paket tidak boleh mengandung spasi.")

    
        server = ip_pool.id_server if ip_pool else None
        if server:
            qs = Paket.objects.filter(
                name=name,
                id_ip_pool__id_server=server
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('name', "Nama Paket sudah ada di server ini, silakan gunakan nama lain.")

        return cleaned_data
    
class ipPoolForm(forms.ModelForm):
    class Meta: 
        model = IPPool
        fields = ['name', 'ip_range', 'id_server']
        widgets = {
            'id_server': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Ip pool'}),
            'ip_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 192.168.0.1 - 192.168.0.255'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        server = cleaned_data.get('id_server')

        if not name or not server:
            return cleaned_data  # biar error field lain tetap muncul

        # cek spasi
        if " " in name:
            self.add_error('name',"Nama IP Pool tidak boleh mengandung spasi.")

        # cek duplikat dalam server yang sama
        qs = IPPool.objects.filter(name=name, id_server=server)
        if self.instance.pk:  # kalau sedang update/edit, exclude dirinya sendiri
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            self.add_error('name',"Nama IP Pool sudah ada pada server ini, silakan pilih nama lain.")

        return cleaned_data
        
        
   
        

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['id_paket', 'name', 'address', 'email', 'phone', 'pppoe', 'password', 'lat', 'long', 'local_ip']
        widgets = {
            'id_paket': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Pelanggan'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Alamat Pelanggan'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Email Pelanggan'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan No Hp Pelanggan'}),
            'pppoe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan id pppoe Pelanggan'}),
            'password': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan password id pppoe Pelanggan'}),
            'local_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan local IP untuk client'}),
            'lat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan latitude lokasi'}),
            'long': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan longitude lokasi'}),
        }

    def clean_pppoe(self):
        pppoe = self.cleaned_data.get('pppoe')
        if not pppoe:
            return pppoe

        if ' ' in pppoe:
            raise forms.ValidationError("ID PPPoE tidak boleh mengandung spasi.")
        return pppoe

    def clean(self):
        cleaned_data = super().clean()
        pppoe = cleaned_data.get('pppoe')
        paket = cleaned_data.get('id_paket')

        # kalau pppoe atau paket kosong, skip validasi tambahan
        if not pppoe or not paket:
            return cleaned_data  

        ip_pool = getattr(paket, 'id_ip_pool', None)
        server = getattr(ip_pool, 'id_server', None)

        if server:
            qs = Client.objects.filter(
                pppoe=pppoe,
                id_paket__id_ip_pool__id_server=server
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error('pppoe', "ID PPPoE ini sudah digunakan di server ini, silakan pilih yang lain.")

        return cleaned_data
