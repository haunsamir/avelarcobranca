# Generated by Django 5.0.6 on 2024-06-13 12:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0028_remove_materialconvalescente_colaborador_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialconvalescente',
            name='colaborador',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]