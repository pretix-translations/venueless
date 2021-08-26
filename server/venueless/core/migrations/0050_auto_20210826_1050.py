# Generated by Django 3.2.6 on 2021-08-26 08:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0049_streamingserver"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="streamingserver",
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="WorldView",
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
                ("start", models.DateTimeField(auto_now_add=True)),
                ("end", models.DateTimeField(db_index=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="world_views",
                        to="core.user",
                    ),
                ),
                (
                    "world",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="views",
                        to="core.world",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="worldview",
            index=models.Index(fields=["start"], name="core_worldv_start_b8ddc0_idx"),
        ),
    ]
