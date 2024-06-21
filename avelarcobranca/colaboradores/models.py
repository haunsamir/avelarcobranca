from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('administrador', 'Administrador'),
        ('colaborador', 'Colaborador'),
    )

    COLABORADOR_TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('atrasado', 'Atrasado'),
        ('filial', 'Filial'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    colaborador_type = models.CharField(max_length=20, choices=COLABORADOR_TYPE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username

class ListaDistribuida(models.Model):
    id_lista = models.UUIDField(default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=10)
    nome = models.CharField(max_length=255, null=True, blank=True)
    nome_lista = models.CharField(max_length=255, null=True, blank=True)
    lista = models.TextField(null=True, blank=True)
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    tipo_lista = models.CharField(max_length=20, choices=[
        ('regular', 'Regular'),
        ('atrasado', 'Atrasado'),
        ('filial', 'Filial')
    ])
    data_distribuicao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.nome_lista}"

class Interacao(models.Model):
    codigo_cliente = models.CharField(max_length=10)
    legenda = models.CharField(max_length=50, choices=[
        ('ok_pix', 'Ok/Pix'),
        ('tentativa_recolhimento', 'Tentativa recolhimento'),
        ('outra_data', 'Outra data'),
        ('terceiro_sem_data', 'Terceiro/Sem data'),
        ('sem_contato', 'Sem contato'),
        ('cancelado', 'Cancelado'),
        ('ja_tratado', 'Já tratado'),
        ('empresarial', 'Empresarial'),
    ], blank=True, null=True)
    motivo = models.CharField(max_length=50, choices=[
        ('sem_dinheiro', 'Sem dinheiro'),
        ('mes_que_vem', 'Mês que vem'),
    ], blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    data_interacao = models.DateTimeField(auto_now=True)
    lista_distribuida_id = models.UUIDField(default=uuid.uuid4, editable=False)
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.codigo_cliente} - {self.legenda} - {self.motivo}"

class Evento(models.Model):
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10)
    observacao = models.TextField()
    data = models.DateField()

    def __str__(self):
        return f"{self.codigo} - {self.data}"

class Caderno(models.Model):
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    codigo_cliente = models.CharField(max_length=20)
    data_baixa = models.DateField()

    def __str__(self):
        return f"{self.colaborador.username} - {self.codigo_cliente}"

class PagamentoTransferido(models.Model):
    codigo_cliente = models.CharField(max_length=20)
    nome_titular = models.CharField(max_length=100)
    data_pgto = models.DateField()
    parcela = models.CharField(max_length=7)  # 'mm/aa'
    criado_em = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Adicionando o campo colaborador

    def __str__(self):
        return f"{self.codigo_cliente} - {self.nome_titular} - {self.parcela}"


from django.conf import settings
from django.db import models

class PagamentoRemovido(models.Model):
    data_exclusao = models.DateTimeField(auto_now_add=True)
    codigo_cliente = models.CharField(max_length=20)
    nome_cliente = models.CharField(max_length=100)
    motivo = models.TextField()
    parcela = models.CharField(max_length=20, null=True, blank=True)  # Adicionando o campo parcela
    colaborador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pagamentos_removidos')  # Quem removeu
    colaborador_original = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='pagamentos_transferidos')  # Dono original
    visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_cliente} - {self.nome_cliente} - {self.motivo} - {self.parcela}"

from django.conf import settings
from django.db import models
# models.py
class MaterialConvalescente(models.Model):
    codigo_cliente = models.CharField(max_length=100)
    data_pagamento = models.DateField()
    material = models.CharField(max_length=100)
    parcelas = models.IntegerField()  # Alterado para armazenar a quantidade de parcelas
    colaborador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.codigo_cliente
