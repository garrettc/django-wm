# Generated by Django 4.1 on 2022-08-27 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mentions", "0007_dashboardpermissionproxy"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="webmention",
            options={"ordering": ["-created_at"]},
        ),
    ]