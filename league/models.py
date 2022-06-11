from decimal import Decimal
from email.policy import default
from django.contrib.postgres.fields import CICharField
from django.db import models
from django_countries.fields import CountryField
from league.constants import PlayerPosition, TransferStatus
from oscsettings.models import LeagueSettings
from users.models import User


def get_initial_player_value():
    return LeagueSettings.load().initial_player_value

def get_initial_team_budget():
    return LeagueSettings.load().initial_team_budget

def get_default_country():
    return LeagueSettings.load().default_country


class Team(models.Model):
    owner = models.OneToOneField(User, related_name='team', on_delete=models.CASCADE)
    name = CICharField(max_length=100, unique=True)
    country = CountryField(default=get_default_country)
    budget = models.DecimalField(max_digits=65, decimal_places=2, default=get_initial_team_budget)


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=10, choices=PlayerPosition.choices, default=PlayerPosition.DEFENDER)
    age = models.PositiveIntegerField()
    country = CountryField(default=get_default_country)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=65, decimal_places=2, default=get_initial_player_value)


class Transfer(models.Model):
    seller = models.ForeignKey(Team, null=True, blank=True, related_name='sold_players', on_delete=models.SET_NULL)
    buyer = models.ForeignKey(Team, null=True, blank=True, related_name='bought_players', on_delete=models.SET_NULL)
    player = models.ForeignKey(Player, null=True, blank=True, related_name='transfers', on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=65, decimal_places=2)
    status = models.CharField(max_length=8, choices=TransferStatus.choices, default=TransferStatus.PENDING)
