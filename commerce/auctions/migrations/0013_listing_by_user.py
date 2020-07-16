# Generated by Django 3.0.8 on 2020-07-15 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20200715_0518'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='by_user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='my_listings', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]