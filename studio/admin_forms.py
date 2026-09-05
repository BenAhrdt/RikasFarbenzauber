from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .access import FIELDS

class AccountForm(forms.ModelForm):
    password1=forms.CharField(label='Neues Passwort',required=False,widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    password2=forms.CharField(label='Passwort wiederholen',required=False,widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    is_superuser=forms.BooleanField(label='Administrator: Benutzer und Updates verwalten',required=False)
    class Meta:
        model=User
        fields=['username','first_name','is_active','is_superuser']
        labels={'username':'Anmeldename','first_name':'Vorname (optional)','is_active':'Konto ist aktiv'}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.creating=not self.instance.pk
        self.fields['password1'].required=self.creating
        self.fields['password2'].required=self.creating
        for key,label in FIELDS.items():
            self.fields[key]=forms.BooleanField(label=label,required=False,initial=True)
    def clean(self):
        data=super().clean()
        password=data.get('password1')
        if password != data.get('password2'):
            self.add_error('password2','Die Passwörter stimmen nicht überein.')
        if password:
            user=User(username=data.get('username',''),first_name=data.get('first_name',''))
            try:validate_password(password,user)
            except forms.ValidationError as error:self.add_error('password1',error)
        return data
