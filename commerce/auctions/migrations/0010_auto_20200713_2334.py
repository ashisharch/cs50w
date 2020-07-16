# Generated by Django 3.0.8 on 2020-07-13 23:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20200713_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='name',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='watchlist',
            name='user',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='watchlist',
            name='listings',
        ),
        migrations.AddField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='auctions.Listing'),
        ),
    ]