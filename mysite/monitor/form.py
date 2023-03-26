from django import forms
from django.forms import ModelForm
from .models import Host, Time


class HostForm(ModelForm):
    class Meta:
        model = Host
        fields = ('name', 'address', 'port', 'description', 'network',)
        labels = {
            'name': '',
            'address': '',
            'port': '',
            'description': '',
            'network': '',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên Host'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'port': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Port'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả'}),
            'network': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Network'}),
        }


class TimeForm(ModelForm):
    class Meta:
        model = Time
        fields = ('set_hours', 'set_minutes', 'set_seconds',)
        labels = {
            'set_hours': '',
            'set_minutes': '',
            'set_seconds': '',
        }
        widgets = {
            'set_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập giờ'}),
            'set_minutes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập phút'}),
            'set_seconds': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập giây'}),
        }
