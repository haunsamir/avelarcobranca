from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('administrador', 'Administrador'),
        ('colaborador', 'Colaborador'),
    ]

    COLABORADOR_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('atrasado', 'Atrasado'),
        ('filial', 'Filial'),
    ]

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, label='Tipo de Usuário')
    colaborador_type = forms.ChoiceField(choices=COLABORADOR_TYPE_CHOICES, label='Tipo de Colaborador', required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'user_type', 'colaborador_type')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        colaborador_type = cleaned_data.get('colaborador_type')

        if user_type == 'colaborador' and not colaborador_type:
            self.add_error('colaborador_type', 'Este campo é obrigatório para colaboradores.')

        return cleaned_data

from django import forms
from .models import ListaDistribuida, CustomUser

class ListaDistribuidaForm(forms.ModelForm):
    lista = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}))
    nome_lista = forms.CharField(label='Nome da Lista', max_length=255, required=False)  # Campo adicional
    tipo_lista = forms.ChoiceField(choices=[
        ('regular', 'Regular'),
        ('atrasado', 'Atrasado'),
        ('filial', 'Filial')
    ], initial='regular')

    class Meta:
        model = ListaDistribuida
        fields = ['lista', 'tipo_lista']

    colaboradores = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        tipo_lista = kwargs.pop('tipo_lista', 'regular')
        super().__init__(*args, **kwargs)
        self.fields['colaboradores'].queryset = CustomUser.objects.filter(user_type='colaborador', colaborador_type=tipo_lista)
        
        
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

from django import forms
from .models import CustomUser

class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'colaborador_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de Usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'colaborador_type': forms.Select(attrs={'class': 'form-control'}),
        }

from django import forms
from django.contrib.auth.models import User

class ChangePasswordForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(), label="Nova Senha")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirme a Nova Senha")

    class Meta:
        model = User
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data

from django import forms
from .models import MaterialConvalescente

class MaterialConvalescenteForm(forms.ModelForm):
    MATERIAL_CHOICES = [
        ('Andador', 'Andador'),
        ('Cadeira de Banho', 'Cadeira de Banho'),
        ('Muletas Alumínio - Par', 'Muletas Alumínio - Par'),
        ('Cadeira de Rodas', 'Cadeira de Rodas'),
        ('Cadeira de Rodas Grande', 'Cadeira de Rodas Grande'),
        ('Bengala', 'Bengala'),
        ('Muleta Canadense - Par', 'Muleta Canadense - Par'),
        ('Bota Ortopédica', 'Bota Ortopédica'),
        ('Cadeira de Banho Grande', 'Cadeira de Banho Grande'),
    ]

    material = forms.ChoiceField(choices=MATERIAL_CHOICES)

    class Meta:
        model = MaterialConvalescente
        fields = ['codigo_cliente', 'data_pagamento', 'material', 'parcelas']
        widgets = {
            'codigo_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'material': forms.Select(attrs={'class': 'form-control'}),
            'parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
        }
