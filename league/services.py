from decimal import Decimal
from random import randint
from typing import Optional
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, PermissionDenied
from league.models import Team, Player, Transfer
from league.constants import TransferStatus
from users.models import User

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