# Generated by Django 3.0.8 on 2020-07-13 23:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_auto_20200713_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='being_watched', to='auctions.Listing'),
        ),
        migrations.RemoveField(
            model_name='watchlist',
            name='user',
        ),
        migrations.AddField(
            model_name='watchlist',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='watchlist', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
