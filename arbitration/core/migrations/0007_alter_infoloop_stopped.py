# Generated by Django 4.1.7 on 2023-02-27 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_infoloop_stopped'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infoloop',
            name='stopped',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Stopped date'),
        ),
    ]
