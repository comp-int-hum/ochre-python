# Generated by Django 4.0.10 on 2023-04-16 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ochre', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='source_id',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='source_type',
        ),
        migrations.AddField(
            model_name='annotation',
            name='machinelearningmodel',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='ochre.machinelearningmodel'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='primarysource',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='ochre.primarysource'),
        ),
    ]