# Generated by Django 3.2.11 on 2022-02-08 20:59

import datetime

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0051_auto_20211125_0444"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
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
                ("code", models.CharField(max_length=30, unique=True)),
                (
                    "user_type",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "User"), (2, "Organization")], default=1
                    ),
                ),
                (
                    "ordering",
                    models.PositiveIntegerField(
                        default=0,
                        help_text='Relative ordering of the record. Lower values have higher priority (will be first in the list). Records with same ordering will be sorted by "Display name" and "Code". Please set with gaps for different records for easy reordering (e.g. 5, 10, 15, but not 5, 6, 7).',
                    ),
                ),
                ("display_name", models.CharField(max_length=100)),
                ("storage_mb", models.PositiveIntegerField(default=10)),
                ("storage_keep_versions", models.PositiveIntegerField(default=10)),
                ("job_minutes", models.PositiveIntegerField(default=10)),
                ("can_add_storage", models.BooleanField(default=False)),
                ("can_add_job_minutes", models.BooleanField(default=False)),
                ("is_external_db_supported", models.BooleanField(default=False)),
                (
                    "can_configure_repackaging_cache_expire",
                    models.BooleanField(default=False),
                ),
                (
                    "min_repackaging_cache_expire",
                    models.DurationField(
                        default=datetime.timedelta(seconds=3600),
                        validators=[
                            django.core.validators.MinValueValidator(
                                datetime.timedelta(seconds=60)
                            )
                        ],
                    ),
                ),
                (
                    "synchronizations_per_months",
                    models.PositiveIntegerField(default=30),
                ),
                ("is_public", models.BooleanField(default=False)),
                ("is_default", models.BooleanField(default=False)),
            ],
            options={
                "ordering": (
                    "ordering",
                    "display_name",
                    "code",
                )
            },
        ),
        migrations.CreateModel(
            name="ExtraPackageType",
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
                ("code", models.CharField(max_length=30, unique=True)),
                ("display_name", models.CharField(max_length=100)),
                ("is_public", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="ExtraPackageTypeJobMinutes",
            fields=[
                (
                    "extrapackagetype_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="subscription.extrapackagetype",
                    ),
                ),
                ("minutes", models.PositiveIntegerField()),
            ],
            bases=("subscription.extrapackagetype",),
        ),
        migrations.CreateModel(
            name="ExtraPackageTypeStorage",
            fields=[
                (
                    "extrapackagetype_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="subscription.extrapackagetype",
                    ),
                ),
                ("megabytes", models.PositiveIntegerField()),
            ],
            bases=("subscription.extrapackagetype",),
        ),
        migrations.CreateModel(
            name="ExtraPackage",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="subscription.extrapackagetype",
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_packages",
                        to="core.useraccount",
                    ),
                ),
            ],
        ),
    ]
