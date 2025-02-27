# Generated by Django 4.0.6 on 2022-07-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("allow_outgoing_webmentions", models.BooleanField(default=False)),
                ("author", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=64)),
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
