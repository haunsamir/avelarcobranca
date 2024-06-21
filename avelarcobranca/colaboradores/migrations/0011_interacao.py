# Generated by Django 5.0.6 on 2024-06-03 11:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0010_listadistribuida_nome_lista_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_cliente', models.CharField(max_length=10)),
                ('legenda', models.CharField(blank=True, choices=[('ok_pix', 'Ok/Pix'), ('tentativa_recolhimento', 'Tentativa recolhimento'), ('outra_data', 'Outra data'), ('terceiro_sem_data', 'Terceiro/Sem data'), ('sem_contato', 'Sem contato'), ('cancelado', 'Cancelado'), ('ja_tratado', 'Já tratado'), ('empresarial', 'Empresarial')], max_length=50, null=True)),
                ('motivo', models.CharField(blank=True, choices=[('sem_dinheiro', 'Sem dinheiro'), ('mes_que_vem', 'Mês que vem')], max_length=50, null=True)),
                ('data_interacao', models.DateTimeField(auto_now=True)),
                ('colaborador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lista_distribuida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='colaboradores.listadistribuida')),
            ],
        ),
    ]