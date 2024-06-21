# Generated by Django 5.0.6 on 2024-05-31 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0003_listadistribuida'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='nome_completo',
        ),
        migrations.AddField(
            model_name='customuser',
            name='colaborador_type',
            field=models.CharField(blank=True, choices=[('regular', 'Regular'), ('atrasado', 'Atrasado'), ('filial', 'Filial')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('administrador', 'Administrador'), ('colaborador', 'Colaborador')], max_length=20),
        ),
    ]
