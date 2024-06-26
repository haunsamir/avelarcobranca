# Generated by Django 5.0.6 on 2024-05-31 19:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0004_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listadistribuida',
            name='distribuido_para',
        ),
        migrations.AddField(
            model_name='listadistribuida',
            name='colaborador',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listas_distribuidas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listadistribuida',
            name='tipo_lista',
            field=models.CharField(choices=[('regular', 'Regular'), ('atrasado', 'Atrasado'), ('filial', 'Filial')], default='regular', max_length=10),
        ),
    ]
