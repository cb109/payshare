# Generated by Django 2.0.3 on 2018-06-20 21:35

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Liquidation = apps.get_model("purchases", "Liquidation")

    for liquidation in Liquidation.objects.all():
        descr = liquidation.description
        liquidation.name = descr if descr is not None else ""
        liquidation.save()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0014_collective_currency_symbol'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='description',
        ),
        migrations.AddField(
            model_name='liquidation',
            name='name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.RemoveField(
            model_name='liquidation',
            name='description',
        ),
    ]
