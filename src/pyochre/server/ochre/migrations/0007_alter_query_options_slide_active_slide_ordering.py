# Generated by Django 4.2 on 2023-05-30 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0006_remove_annotation_primarysources_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'verbose_name_plural': 'queries'},
        ),
        migrations.AddField(
            model_name='slide',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='slide',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
    ]
