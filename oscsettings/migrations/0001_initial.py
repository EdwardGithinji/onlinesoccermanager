# Generated by Django 4.0.5 on 2022-06-11 20:52

from decimal import Decimal
from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initial_player_value', models.DecimalField(decimal_places=2, default=Decimal('1000000'), max_digits=65)),
                ('initial_team_budget', models.DecimalField(decimal_places=2, default=Decimal('5000000'), max_digits=65)),
                ('default_country', django_countries.fields.CountryField(default='KE', max_length=2)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
