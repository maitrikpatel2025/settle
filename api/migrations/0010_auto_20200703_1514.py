# Generated by Django 3.0.7 on 2020-07-03 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20200701_2255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apartment',
            name='price_rate_unit',
        ),
        migrations.RemoveField(
            model_name='frame',
            name='price_rate_unit',
        ),
        migrations.RemoveField(
            model_name='hostel',
            name='price_rate_unit',
        ),
        migrations.RemoveField(
            model_name='house',
            name='price_rate_unit',
        ),
        migrations.RemoveField(
            model_name='office',
            name='price_rate_unit',
        ),
        migrations.RemoveField(
            model_name='room',
            name='price_rate_unit',
        ),
    ]
