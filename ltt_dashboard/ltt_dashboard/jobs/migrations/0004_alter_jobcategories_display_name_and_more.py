# Generated by Django 4.0.6 on 2022-07-07 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_alter_job_name_alter_jobcategories_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobcategories',
            name='display_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='jobcategories',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='jobtype',
            name='identifier',
            field=models.CharField(choices=[('internship', 'Internship'), ('part_time', 'Part Time'), ('full_time', 'Full Time')], max_length=50, verbose_name='Identifier'),
        ),
    ]
