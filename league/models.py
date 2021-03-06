from typing import Any
from decimal import Decimal
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

    def __str__(self):
        return self.name

    @property
    def value(self):
        value = self.players.aggregate(total_value=models.Sum('value'))['total_value']
        return value if value is not None else Decimal(0)


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=10, choices=PlayerPosition.choices, default=PlayerPosition.DEFENDER)
    age = models.PositiveIntegerField()
    country = CountryField(default=get_default_country)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=65, decimal_places=2, default=get_initial_player_value)

    def __str__(self):
        return ' '.join(filter(None, (self.first_name, self.last_name)))


class Transfer(models.Model):
    seller = models.ForeignKey(Team, null=True, blank=True, related_name='sold_players', on_delete=models.SET_NULL)
    buyer = models.ForeignKey(Team, null=True, blank=True, related_name='bought_players', on_delete=models.SET_NULL)
    player = models.ForeignKey(Player, null=True, blank=True, related_name='transfers', on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=65, decimal_places=2)
    status = models.CharField(max_length=8, choices=TransferStatus.choices, default=TransferStatus.PENDING)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.id:
            self.status = TransferStatus.PENDING
        if self.status == TransferStatus.PENDING:
            if self.player is not None:
                self.seller = self.player.team
            self.buyer = None
        super().save(**kwargs)
