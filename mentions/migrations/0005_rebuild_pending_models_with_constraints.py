# Generated with Django 4.0.2
# Manually edited to squash model deletion and creation steps in a single file.
# PendingIncomingMWebmention and PendingOutgoingContent models are deleted
# and recreated so we can introduce unique constraints on each. Any existing
# instances of those models will be deleted.


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mentions", "0004_simplemention_post_type_webmention_post_type_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PendingIncomingWebmention",
        ),
        migrations.DeleteModel(
            name="PendingOutgoingContent",
        ),
        migrations.CreateModel(
            name="PendingIncomingWebmention",
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
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "source_url",
                    models.URLField(
                        help_text="The URL of the content that mentions your content."
                    ),
                ),
                (
                    "target_url",
                    models.URLField(
                        help_text="The URL of the page on your server that is being mentioned."
                    ),
                ),
                (
                    "sent_by",
                    models.URLField(help_text="The origin of the webmention request."),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PendingOutgoingContent",
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
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "absolute_url",
                    models.URLField(
                        help_text="URL on our server where the content can be found.",
                        unique=True,
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Text that may contain mentionable links. (retrieved via MentionableMixin.all_text())"
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="pendingincomingwebmention",
            constraint=models.UniqueConstraint(
                fields=("source_url", "target_url"),
                name="unique_source_url_per_target_url",
            ),
        ),
    ]
