import string
from decimal import Decimal
from random import randint, choices
from typing import Optional
from faker import Faker
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, PermissionDenied
from league.constants import TransferStatus, PlayerPosition
from league.models import Team, Player, Transfer

User = get_user_model()

NUMBER_OF_GOALKEEPERS = 3
NUMBER_OF_MIDFIELDERS = 6
NUMBER_OF_DEFENDERS = 6
NUMBER_OF_ATTACKERS = 5


def generate_team_with_players(user: User):
    fake = Faker()
    team_names_set = set(Team.objects.values_list('name', flat=True))
    abbrev_size = 10
    team_name = fake.city() + ' ' + ''.join(choices(string.ascii_uppercase, k=abbrev_size))

    while team_name in team_names_set:
        abbrev_size += 1
        team_name = fake.city() + ' ' + ''.join(choices(string.ascii_uppercase, k=abbrev_size))

    team = Team.objects.create(owner=user, name=team_name)
    players_list = []

    for i in range(20):
        if 0 <= i < 3:
            player_position = PlayerPosition.GOALKEEPER
        elif 3 <= i < 9:
            player_position = PlayerPosition.DEFENDER
        elif 9 <= i < 15:
            player_position = PlayerPosition.MIDFIELDER
        else:
            player_position = PlayerPosition.ATTACKER

        player = Player(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            position=player_position,
            team=team,
            age=randint(18,40)
            )
        players_list.append(player)

    Player.objects.bulk_create(players_list)

@transaction.atomic
def team_update(team: Team, user: User, name:Optional[str] = None, country: Optional[str] = None) -> Player:

    if user != team.owner:
        raise PermissionDenied({'detail':'only team owner can update team details'})
    if name:
        if Team.objects.filter(name=name).exists():
            raise ValidationError({'detail': 'A team already exists with that name, choose another'})
        team.name = name
    if country:
        team.country = country
    team.save()
    return team


@transaction.atomic
def player_update(
    player: Player,
    user: User,
    first_name:Optional[str] = None,
    last_name:Optional[str] = None,
    country: Optional[str] = None
    ) -> Player:

    if player.team.owner != user:
        raise PermissionDenied({'detail': 'Only team owner of team player belongs to can update player details'})

    if first_name:
        player.first_name = first_name
    if last_name:
        player.last_name = last_name
    if country:
        player.country = country
    player.save()
    return player


@transaction.atomic
def player_transfer_create(player_id: int, price: Decimal, user: User):
    player = get_object_or_404(Player, pk=player_id)
    if player.team.owner != user:
        raise PermissionDenied({'detail': 'Only team owner of team player belongs to can transfer player'})

    if Transfer.objects.filter(player=player, status=TransferStatus.PENDING).exists():
        raise ValidationError({'detail': 'player is already on the transfer list'})
    seller = user.team
    transfer = Transfer.objects.create(player=player, seller=seller, price=price)

    return transfer


@transaction.atomic
def player_buy(player_id, user: User):
    if not user.is_team_owner:
        raise PermissionDenied({'detail': 'only users who own a team can buy a player'})
    player = get_object_or_404(Player, pk=player_id)
    try:
        transfer = Transfer.objects.get(player=player, status=TransferStatus.PENDING)
    except Transfer.DoesNotExist:
        raise ValidationError({'detail': 'this player is not available for transfer'})
    except Transfer.MultipleObjectsReturned:
        raise ValidationError({
            'detail': 'this player has multiple pending transfers on market. contact admin for further assistance'
            })
    buyer = user.team
    seller = player.team
    if seller == buyer:
        raise PermissionDenied({'detail': 'team selling a player cannot buy its own player'})
    if transfer.price > buyer.budget:
        raise ValidationError({'detail': 'you do not have enough funds to buy this player'})

    player_value_markup = Decimal(1 + (randint(10, 100) / 100))
    seller.budget += transfer.price
    buyer.budget -= transfer.price
    player.value *= player_value_markup
    player.team = buyer
    transfer.status = TransferStatus.COMPLETE
    transfer.buyer = buyer

    seller.save()
    buyer.save()
    player.save()
    transfer.save()

    return player


@transaction.atomic
def buy_player_complete_transfer(transfer_id, user: User):
    if not user.is_team_owner:
        raise PermissionDenied({'detail': 'only users who own a team can buy a player'})
    buyer = user.team
    transfer = get_object_or_404(Transfer, pk=transfer_id)
    seller = transfer.seller
    player = transfer.player
    if seller == buyer:
        raise PermissionDenied({'detail': 'team selling a player cannot buy its own player'})
    if transfer.status == TransferStatus.COMPLETE:
        raise ValidationError({'detail': 'provided transfer has already been completed'})
    if transfer.price > buyer.budget:
        raise ValidationError({'detail': 'you do not have enough funds to buy this player'})

    player_value_markup = randint(10, 100)

    seller.budget += transfer.price
    buyer.budget -= transfer.price
    player.value += (player.value * Decimal((player_value_markup / 100)))
    player.team = buyer
    transfer.status = TransferStatus.COMPLETE
    transfer.buyer = buyer

    seller.save()
    buyer.save()
    player.save()
    transfer.save()

    return transfer
