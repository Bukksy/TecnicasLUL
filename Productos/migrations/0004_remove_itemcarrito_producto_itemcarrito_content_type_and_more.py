# Generated by Django 5.1.7 on 2025-05-22 20:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Productos', '0003_detalleordenonepiece_detalleordenpokemon'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemcarrito',
            name='producto',
        ),
        migrations.AddField(
            model_name='itemcarrito',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='itemcarrito',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
