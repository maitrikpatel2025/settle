# Generated by Django 3.0.7 on 2020-06-30 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20200630_2100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frame',
            name='area',
        ),
        migrations.RemoveField(
            model_name='frame',
            name='length',
        ),
        migrations.RemoveField(
            model_name='frame',
            name='length_unit',
        ),
        migrations.RemoveField(
            model_name='frame',
            name='width',
        ),
        migrations.RemoveField(
            model_name='office',
            name='area',
        ),
        migrations.RemoveField(
            model_name='office',
            name='length',
        ),
        migrations.RemoveField(
            model_name='office',
            name='length_unit',
        ),
        migrations.RemoveField(
            model_name='office',
            name='width',
        ),
        migrations.AddField(
            model_name='apartment',
            name='price_rate_unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='frame',
            name='price_rate_unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='hostel',
            name='price_rate_unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='price_rate_unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='office',
            name='price_rate_unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='available_for',
            field=models.CharField(choices=[('sale', 'Sale'), ('rent', 'Rent')], max_length=5),
        ),
        migrations.DeleteModel(
            name='Hall',
        ),
    ]