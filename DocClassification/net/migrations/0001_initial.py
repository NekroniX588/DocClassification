# Generated by Django 3.1.7 on 2021-06-22 17:16

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Queries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attach', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='collection'), upload_to='')),
            ],
        ),
    ]