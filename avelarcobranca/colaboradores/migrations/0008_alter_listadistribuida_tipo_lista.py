# Generated by Django 5.0.6 on 2024-05-31 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0007_alter_listadistribuida_colaborador'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listadistribuida',
            name='tipo_lista',
            field=models.CharField(choices=[('regular', 'Regular'), ('atrasado', 'Atrasado'), ('filial', 'Filial')], max_length=20),
        ),
    ]
