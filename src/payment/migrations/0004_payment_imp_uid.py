# Generated by Django 5.1.1 on 2024-10-01 14:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0003_rename_username_payment_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="imp_uid",
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
