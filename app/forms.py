from django import forms
import ipaddress
from .models import Gateway, Server, Paket, IPPool, Client


#server
class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'host', 'username', 'password', 'genieacs', 'lat', 'long']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Server'}),
            'host': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Host IP'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Password'}),
            'genieacs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan IP GenieACS, Kosongkan Jika tidak ada'}),
            'lat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan latitude lokasi'}),
            'long': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan longitude lokasi'}),
        }
class GatewayForm(forms.ModelForm):
    parent_choice = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Gateway
        fields = ['name', 'lat', 'long']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Gateway'}),
            'lat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan latitude lokasi'}),
            'long': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan longitude lokasi'}),
        }

    def __init__(self, *args, **kwargs):
        server = kwargs.pop('server', None)  # ambil server dari view
        super().__init__(*args, **kwargs)

        choices = []
        if server:
            # opsi server
            choices.append((f"server-{server.id}", f"Server: {server.name}"))

            # ODP/Gateway yang hanya milik server ini
            for gw in Gateway.objects.filter(server=server):
                choices.append((f"gateway-{gw.id}", f"ODP: {gw.name}"))

        self.fields['parent_choice'].choices = choices




class PaketForm(forms.ModelForm):
    UNIT_CHOICES = [
    ('K', 'Kbps'),
    ('M', 'Mbps'),
    ('G', 'Gbps'),
    ]
    upload_rate = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Upload'})
    )
    upload_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        initial='M',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    download_rate = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Download'})
    )
    download_unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        initial='M',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta : 
        model = Paket
        fields = ['name', 'price', 'id_ip_pool']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Paket'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh 200000'}),
            'limit': forms.HiddenInput(), 
            'id_ip_pool': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # kalau edit (instance ada), parse limit "10M/2M" -> download=10, upload=2
        if self.instance and self.instance.pk and self.instance.limit:
            try:
                down, up = self.instance.limit.split("/")
                # ambil angka & satuan (misal "10M" -> 10 + M)
                self.fields['download_rate'].initial = int(''.join(filter(str.isdigit, down)))
                self.fields['download_unit'].initial = ''.join(filter(str.isalpha, down))

                self.fields['upload_rate'].initial = int(''.join(filter(str.isdigit, up)))
                self.fields['upload_unit'].initial = ''.join(filter(str.isalpha, up))
            except Exception:
                pass  # kalau format limit aneh, biarin kosong

    def clean_limit(self):
        limit = self.cleaned_data.get('limit')
        if limit:
            return limit.upper()
        return limit

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        ip_pool = cleaned_data.get('id_ip_pool')

        up = cleaned_data.get('upload_rate') or 0
        up_unit = cleaned_data.get('upload_unit') or 'M'
        down = cleaned_data.get('download_rate') or 0
        down_unit = cleaned_data.get('download_unit') or 'M'

        cleaned_data['limit'] = f"{down}{down_unit}/{up}{up_unit}".upper()

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
    

USABLE_PER_24 = 253
MAX_16_PREFIX = 256 * USABLE_PER_24  # 64768

def generate_ip_range(prefix: str, count: int) -> str:
    if count <= 0:
        raise ValueError("Jumlah host harus lebih dari 0.")

    parts = prefix.split('.')
    parts = [p.strip() for p in parts if p.strip() != ""]

    if len(parts) == 2:
        # max untuk /16 (dengan aturan host .2 sampai .254 per /24)
        if count > MAX_16_PREFIX:
            raise ValueError(f"Jumlah host terlalu besar untuk prefix {prefix} (maks {MAX_16_PREFIX}).")
        start_ip = ipaddress.IPv4Address(f"{parts[0]}.{parts[1]}.0.2")
        end_ip = start_ip + (count - 1)
        # pastikan masih di dalam same /16
        if f"{end_ip}".split('.')[0:2] != [parts[0], parts[1]]:
            # defensif: meskipun kita sudah memeriksa count, ini safety check
            raise ValueError(f"Range melebihi prefix {prefix}.")
        return f"{start_ip} - {end_ip}"

    elif len(parts) == 3:
        # hanya dalam /24
        if count > USABLE_PER_24:
            raise ValueError(f"Jumlah host terlalu besar untuk prefix {prefix} (/24), maks {USABLE_PER_24}.")
        start_ip = ipaddress.IPv4Address(f"{parts[0]}.{parts[1]}.{parts[2]}.2")
        end_ip = start_ip + (count - 1)
        return f"{start_ip}-{end_ip}"

    else:
        raise ValueError("Prefix harus 2 atau 3 oktet (contoh: 10.10 atau 10.10.10).")


class ipPoolForm(forms.ModelForm):
    prefix = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 10.10 atau 10.10.10'})
    )
    count = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah host, contoh 200'})
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {})
        if instance and instance.ip_range:
            try:
                start_ip, _ = instance.ip_range.split(" - ")
                parts = start_ip.split(".")
                if parts[2] == "0":
                    initial.setdefault("prefix", f"{parts[0]}.{parts[1]}")
                else:
                    initial.setdefault("prefix", f"{parts[0]}.{parts[1]}.{parts[2]}")
            except Exception:
                pass
        if instance and instance.total_ips:
            initial.setdefault("count", instance.total_ips)
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    class Meta:
        model = IPPool
        fields = ['name', 'id_server']
        widgets = {
            'id_server': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan Nama Ip pool'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        server = cleaned_data.get('id_server')
        prefix = cleaned_data.get('prefix')
        count = cleaned_data.get('count')

        # validasi awal (misal name/server)
        if not name or not server:
            return cleaned_data

        # cek spasi di name
        if " " in name:
            self.add_error('name', "Nama IP Pool tidak boleh mengandung spasi.")

        # cek duplikat
        qs = IPPool.objects.filter(name=name, id_server=server)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            self.add_error('name', "Nama IP Pool sudah ada pada server ini, silakan pilih nama lain.")

        # validasi prefix & count -> generate range
        if prefix and count is not None:
            try:
                ip_range = generate_ip_range(prefix, count)
                cleaned_data['ip_range'] = ip_range
            except ValueError as ve:
                # tambahkan error pada field prefix atau count
                self.add_error('prefix', str(ve))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.ip_range = self.cleaned_data.get('ip_range', '')
        instance.total_ips = self.cleaned_data.get('count') or 0
        if commit:
            instance.save()
        return instance
        

class ClientForm(forms.ModelForm):

    gateway_choice = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(gw.id, f"{gw.name}") for gw in Gateway.objects.all()]
        self.fields['gateway_choice'].choices = choices

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
