# Generated by Django 4.1.9 on 2023-07-04 11:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mailroom.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "dtm_created",
                    models.DateTimeField(auto_now_add=True, verbose_name="DTM Created"),
                ),
                (
                    "dtm_updated",
                    models.DateTimeField(auto_now=True, verbose_name="DTM Updated"),
                ),
                ("slug", models.CharField(max_length=16, unique=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "firstname",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=64,
                        null=True,
                        verbose_name="First Name",
                    ),
                ),
                (
                    "lastname",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=64,
                        null=True,
                        verbose_name="Last Name",
                    ),
                ),
                ("email", models.EmailField(max_length=255, unique=True)),
                ("username", models.CharField(max_length=64)),
                ("domain", models.CharField(max_length=255)),
            ],
            options={
                "db_table": "mailroom_contact",
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "dtm_created",
                    models.DateTimeField(auto_now_add=True, verbose_name="DTM Created"),
                ),
                (
                    "dtm_updated",
                    models.DateTimeField(auto_now=True, verbose_name="DTM Updated"),
                ),
                ("slug", models.CharField(max_length=16, unique=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="messages_from",
                        to="mailroom.contact",
                    ),
                ),
                (
                    "to",
                    models.ManyToManyField(
                        related_name="messages_to", to="mailroom.contact"
                    ),
                ),
                (
                    "cc",
                    models.ManyToManyField(
                        related_name="messages_cc", to="mailroom.contact"
                    ),
                ),
                (
                    "bcc",
                    models.ManyToManyField(
                        related_name="messages_bcc", to="mailroom.contact"
                    ),
                ),
                ("subject", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("sent", models.DateTimeField(blank=True, default=None, null=True)),
                (
                    "ref_model",
                    models.CharField(
                        blank=True, default=None, max_length=64, null=True
                    ),
                ),
                (
                    "ref_slug",
                    models.CharField(
                        blank=True, default=None, max_length=16, null=True
                    ),
                ),
            ],
            options={
                "db_table": "mailroom_message",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="BulkMail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "dtm_created",
                    models.DateTimeField(auto_now_add=True, verbose_name="DTM Created"),
                ),
                (
                    "dtm_updated",
                    models.DateTimeField(auto_now=True, verbose_name="DTM Updated"),
                ),
                ("slug", models.CharField(max_length=16, unique=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("sender", models.CharField(max_length=128, verbose_name="From")),
                (
                    "target",
                    models.FileField(
                        blank=True,
                        default=None,
                        null=True,
                        upload_to=mailroom.models.mailroom_bulkmail_target_filepath,
                        verbose_name="To",
                    ),
                ),
                (
                    "target_count",
                    models.IntegerField(default=0, verbose_name="Target Count"),
                ),
                (
                    "cc",
                    models.TextField(
                        blank=True, default=None, null=True, verbose_name="Cc"
                    ),
                ),
                (
                    "bcc",
                    models.TextField(
                        blank=True, default=None, null=True, verbose_name="Bcc"
                    ),
                ),
                ("subject", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("sent", models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                "db_table": "mailroom_bulkmail",
            },
        ),
    ]
