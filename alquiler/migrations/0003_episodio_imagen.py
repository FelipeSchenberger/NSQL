# Generated by Django 5.2 on 2025-04-07 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alquiler', '0002_remove_episodio_reservada_hasta'),
    ]

    operations = [
        migrations.AddField(
            model_name='episodio',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='episodios/'),
        ),
    ]
