# Generated by Django 4.2 on 2023-12-24 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0031_article_abstract'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='annotation',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='documentation',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='documentation',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='machinelearningmodel',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='machinelearningmodel',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='primarysource',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='primarysource',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='query',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='query',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='article',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='researchartifact',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='researchproject',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]