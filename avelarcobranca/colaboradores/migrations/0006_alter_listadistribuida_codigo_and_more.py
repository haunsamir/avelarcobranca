# Generated by Django 5.0.6 on 2024-05-31 19:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0005_remove_listadistribuida_distribuido_para_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listadistribuida',
            name='codigo',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='listadistribuida',
            name='colaborador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='listadistribuida',
            name='tipo_lista',
            field=models.CharField(choices=[('regular', 'Regular'), ('atrasado', 'Atrasado'), ('filial', 'Filial')], max_length=10),
        ),
    ]