# Generated by Django 5.0.6 on 2024-06-07 19:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0022_pagamentotransferido_colaborador'),
    ]

    operations = [
        migrations.CreateModel(
            name='PagamentoRemovido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_exclusao', models.DateTimeField(auto_now_add=True)),
                ('codigo_cliente', models.CharField(max_length=20)),
                ('nome_cliente', models.CharField(max_length=100)),
                ('motivo', models.TextField()),
                ('colaborador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]