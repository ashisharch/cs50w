# Generated by Django 3.0.8 on 2020-07-12 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_bid',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
