from django import forms
from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "value": "",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "value": "",
                "class": "form-control"
            }
        ))


class ProfileChangeForm(forms.ModelForm):
    class Meta():
        model = User
        fields = ("username", "email", "first_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-alternative'


class ChargeForm(forms.Form):
    account = forms.ModelChoiceField(widget=forms.Select,
                                     queryset=User.objects.all())
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
