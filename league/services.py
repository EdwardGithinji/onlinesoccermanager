from decimal import Decimal
from random import randint
from typing import Optional
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from league.models import Team, Player, Transfer
from league.constants import TransferStatus
from users.models import User

@transaction.atomic
def team_update(team: Team, name:Optional[str] = None, country: Optional[str] = None) -> Player:
    ## pending
    ## only team owner can update the team
    if name:
        team.name = name
    if country:
        team.country = country
    team.save()
    return team


@transaction.atomic
def player_update(
    player: Player,
    first_name:Optional[str] = None,
    last_name:Optional[str] = None,
    country: Optional[str] = None
    ) -> Player:

    # pending
    # user requesting player update has a team, and that team is the one the player belongs to


    if first_name:
        player.first_name = first_name
    if last_name:
        player.last_name = last_name
    if country:
        player.country = country
    player.save()
    return player


@transaction.atomic
def player_transfer_create(player_id: int, price: Decimal, user=None):
    # pending
    ## integration of auth to get user creating the transfer
    ## check that user actually has a team
    ## check that user is team owner of the team player belongs to

    try:
        player = Player.objects.get(id=player_id)
        seller = player.team
    except Player.DoesNotExist:
        raise ValidationError({'detail': 'not found. Player does not exist'})

    if Transfer.objects.filter(player=player, status=TransferStatus.PENDING):
        raise ValidationError({'detail': 'player is already on the transfer list'})

    transfer = Transfer.objects.create(player=player, seller=seller, price=price)

    return transfer


@transaction.atomic
def buy_player_complete_transfer(transfer_id, user: User):
    # pending checks
    # user requesting buy is not the seller
    # user requesting buy actually has a team
    # user has budget to afford buying the player
    if not user.is_team_owner:
        raise PermissionDenied({'detail': 'only users who own a team can buy a player'})
    buyer = user.team
    try:
        transfer = Transfer.objects.get(id=transfer_id)
        seller = transfer.seller
        player = transfer.player
    except Transfer.DoesNotExist:
        raise ValidationError({'detail': 'not found. Transfer does not exist'})
    if seller == buyer:
        raise PermissionDenied({'detail': 'team selling a player cannot buy its own player'})
    if transfer.status == TransferStatus.COMPLETE:
        raise ValidationError({'detail': 'provided transfer has already been completed'})
    if transfer.price > buyer.budget:
        raise ValidationError({'detail': 'you do not have enough funds to buy this player'})

    player_value_markup = randint(10, 100)

    seller.budget += transfer.price
    buyer.budget -= transfer.price
    player.value = transfer.price * Decimal((player_value_markup / 100)) + transfer.price
    player.team = buyer
    transfer.status = TransferStatus.COMPLETE
    transfer.buyer = buyer

    seller.save()
    buyer.save()
    player.save()
    transfer.save()

    return transfer