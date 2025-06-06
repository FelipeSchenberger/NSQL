# Generated by Django 5.2 on 2025-04-02 17:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Temporada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('imagen', models.ImageField(upload_to='temporadas/')),
            ],
        ),
        migrations.CreateModel(
            name='Episodio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('disponible', models.BooleanField(default=True)),
                ('reservada_hasta', models.DateTimeField(blank=True, null=True)),
                ('temporada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alquiler.temporada')),
            ],
        ),
    ]
