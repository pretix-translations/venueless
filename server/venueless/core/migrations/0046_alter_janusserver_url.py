# Generated by Django 3.2.3 on 2021-06-01 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0045_auto_20210422_2323"),
    ]

    operations = [
        migrations.AlterField(
            model_name="janusserver",
            name="url",
            field=models.CharField(max_length=200),
        ),
    ]