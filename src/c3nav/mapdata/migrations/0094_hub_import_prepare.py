# Generated by Django 4.2.7 on 2023-12-22 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0093_public_accessrestriction'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
        migrations.AddField(
            model_name='dynamiclocation',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
        migrations.AddField(
            model_name='level',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
        migrations.AddField(
            model_name='locationgroup',
            name='hub_import_type',
            field=models.CharField(blank=True, help_text='assign this group to imported hub locations of this type', max_length=100, null=True, unique=True, verbose_name='hub import type'),
        ),
        migrations.AddField(
            model_name='poi',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
        migrations.AddField(
            model_name='space',
            name='external_url',
            field=models.URLField(blank=True, null=True, verbose_name='external URL'),
        ),
    ]