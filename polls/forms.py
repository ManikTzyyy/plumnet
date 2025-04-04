from django import forms
from .models import Server


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
            'genieacs': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukan IP GenieACS'}),
        }
