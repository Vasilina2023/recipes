# Generated by Django 3.2.3 on 2024-10-02 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('user',), 'verbose_name': 'Подписки', 'verbose_name_plural': 'Подписки'},
        ),
    ]
