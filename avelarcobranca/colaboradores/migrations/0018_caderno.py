# Generated by Django 5.0.6 on 2024-06-03 20:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0017_evento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Caderno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_cliente', models.CharField(max_length=20)),
                ('data_baixa', models.DateField()),
                ('observacao', models.TextField(blank=True, null=True)),
                ('colaborador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
