# Generated by Django 4.0.2 on 2022-03-26 13:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0002_pendingincomingwebmention_pendingoutgoingcontent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simplemention',
            name='published',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='webmention',
            name='published',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]