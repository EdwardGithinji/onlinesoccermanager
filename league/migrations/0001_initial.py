# Generated by Django 4.0.5 on 2022-06-11 20:52

import django.contrib.postgres.fields.citext
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import league.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('position', models.CharField(choices=[('goalkeeper', 'GoalKeeper'), ('defender', 'Defender'), ('midfielder', 'Midfielder'), ('attacker', 'Attacker')], default='defender', max_length=10)),
                ('age', models.PositiveIntegerField()),
                ('country', django_countries.fields.CountryField(default=league.models.get_default_country, max_length=2)),
                ('value', models.DecimalField(decimal_places=2, default=league.models.get_initial_player_value, max_digits=65)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', django.contrib.postgres.fields.citext.CICharField(max_length=100, unique=True)),
                ('country', django_countries.fields.CountryField(default=league.models.get_default_country, max_length=2)),
                ('budget', models.DecimalField(decimal_places=2, default=league.models.get_initial_team_budget, max_digits=65)),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=65)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('complete', 'Complete')], default='pending', max_length=8)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bought_players', to='league.team')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers', to='league.player')),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sold_players', to='league.team')),
            ],
        ),
    ]
