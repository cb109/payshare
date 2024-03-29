# Generated by Django 2.2.10 on 2022-09-17 05:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("purchases", "0021_rename_collective_logo_url_to_logo_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchaseWeight",
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
                ("weight", models.FloatField(default=1.0)),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "purchase",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="purchases.Purchase",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="purchaseweight",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="purchaseweight",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
