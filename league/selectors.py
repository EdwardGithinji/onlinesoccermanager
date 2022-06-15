from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
from league.constants import TransferStatus
from league.filters import TeamFilter, PlayerFilter, TransferFilter
from league.models import Team, Player, Transfer

User = get_user_model()


def user_team_retrieve(user: User):
    return get_object_or_404(Team, owner=user)


def team_list(filters = {}):
    return TeamFilter(filters, Team.objects.all()).qs.order_by('id')


def team_retrieve(team_id: int):
    return get_object_or_404(Team, pk=team_id)


def team_list_players(team_id: int, filters = {}):
    team = get_object_or_404(Team, pk=team_id)
    players_qs = team.players.all()
    sort_option = filters.pop('sort_by', None)
    if sort_option != None:
        return PlayerFilter(filters, players_qs).qs.order_by(sort_option)
    return PlayerFilter(filters, players_qs).qs.order_by('id')


def players_list(filters = {}):
    players_qs = Player.objects.all()
    sort_option = filters.pop('sort_by', None)
    if sort_option != None:
        return PlayerFilter(filters, players_qs).qs.order_by(sort_option)
    return PlayerFilter(filters, players_qs).qs.order_by('id')


def player_retrieve(player_id: int):
    return get_object_or_404(Player, pk=player_id)


def active_transfers_list(filters = {}):
    transfers_qs = Transfer.objects.filter(status=TransferStatus.PENDING)
    sort_option = filters.pop('sort_by', None)
    if sort_option != None:
        return TransferFilter(filters, transfers_qs).qs.order_by(sort_option)
    return TransferFilter(filters, transfers_qs).qs.order_by('id')


def transfer_retrieve_by_player_id(player_id:int):
    try:
        transfer = Transfer.objects.get(player_id=player_id, status=TransferStatus.PENDING)
    except Transfer.DoesNotExist:
        raise NotFound({'detail':'player not found on transfer market'})
    except Transfer.MultipleObjectsReturned:
        raise ValidationError({
            'detail': 'this player has multiple pending transfers on market. contact admin for further assistance'
            })
    return transfer
