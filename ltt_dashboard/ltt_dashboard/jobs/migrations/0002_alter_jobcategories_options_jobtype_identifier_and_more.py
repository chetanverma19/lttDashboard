# Generated by Django 4.0.6 on 2022-07-07 12:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobcategories',
            options={'verbose_name': 'Job Category', 'verbose_name_plural': 'Job Categories'},
        ),
        migrations.AddField(
            model_name='jobtype',
            name='identifier',
            field=models.CharField(choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('internship', 'Internship')], default=django.utils.timezone.now, max_length=50, verbose_name='Identifier'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='jobtype',
            name='display_name',
            field=models.CharField(max_length=100, verbose_name='Display Name'),
        ),
        migrations.AlterField(
            model_name='jobtype',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
    ]
