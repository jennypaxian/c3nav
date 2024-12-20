# Generated by Django 5.0.8 on 2024-12-19 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0122_locationgroup_external_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='door',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='door',
            name='todo',
            field=models.BooleanField(default=False, verbose_name='todo'),
        ),
    ]