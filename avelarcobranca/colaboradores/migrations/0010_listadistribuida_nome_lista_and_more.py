# Generated by Django 5.0.6 on 2024-06-03 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0009_listadistribuida_data_distribuicao'),
    ]

    operations = [
        migrations.AddField(
            model_name='listadistribuida',
            name='nome_lista',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='listadistribuida',
            name='nome',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
