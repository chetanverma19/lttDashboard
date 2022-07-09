# Generated by Django 4.0.6 on 2022-07-09 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='identifier',
        ),
        migrations.AlterField(
            model_name='department',
            name='display_name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Display Text'),
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(db_index=True, max_length=50, unique=True, verbose_name='Department Name'),
        ),
    ]
