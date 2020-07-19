# Generated by Django 3.0.8 on 2020-07-18 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_bid_winning_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='listings', to='auctions.Category'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_url',
            field=models.URLField(null=True),
        ),
    ]
