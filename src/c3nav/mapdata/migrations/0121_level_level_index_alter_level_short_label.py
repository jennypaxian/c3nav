# Generated by Django 5.0.8 on 2024-12-19 08:18

import django.core.validators
import re
from django.db import migrations, models


def set_level_index(apps, schema_editor):
    Level = apps.get_model('mapdata', 'Level')
    for level in Level.objects.all():
        level.level_index = level.short_label
        level.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0120_level_intermediate'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='level_index',
            field=models.CharField(help_text='used for coordinates', max_length=20, null=True, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9._]+\\Z'), 'Enter a valid “level index” consisting of letters, numbers, underscores, dots or hyphens.', 'invalid')], verbose_name='level index')
        ),
        migrations.AlterField(
            model_name='level',
            name='short_label',
            field=models.CharField(help_text='used for the level selector', max_length=20, unique=True, verbose_name='short label'),
        ),
        migrations.RunPython(set_level_index, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='level',
            name='level_index',
            field=models.CharField(help_text='used for coordinates', max_length=20, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9._]+\\Z'), 'Enter a valid “level index” consisting of letters, numbers, underscores, dots or hyphens.', 'invalid')], verbose_name='level index')
        ),
    ]