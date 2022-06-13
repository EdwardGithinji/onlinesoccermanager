from rest_framework.generics import get_object_or_404
from league.constants import TransferStatus
from league.models import Team, Player, Transfer


def team_retrieve(team_id):
    return get_object_or_404(Team, pk=team_id)


def team_list_players(team_id):
    team = get_object_or_404(Team, pk=team_id)
    return team.players.all()


def player_retrieve(player_id):
    return get_object_or_404(Player, pk=player_id)

def transfers_list(status:str=TransferStatus.PENDING):
    return Transfer.objects.filter(status=status)
