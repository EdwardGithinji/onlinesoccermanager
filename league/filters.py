from django_filters import rest_framework as filters
from league.models import Team, Player, Transfer


class TeamFilter(filters.FilterSet):
    class Meta:
        model = Player
        fields = ('country',)


class PlayerFilter(filters.FilterSet):
    class Meta:
        model = Player
        fields = ('position', 'team', 'country')


class TransferFilter(filters.FilterSet):
    position = filters.CharFilter(field_name='player__position')

    class Meta:
        model = Transfer
        fields = ('position', 'seller', 'buyer', 'player')
