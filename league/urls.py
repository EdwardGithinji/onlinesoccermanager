from django.urls import path
from league.views import TeamUpdateRetrieveView, TeamPlayersListView, PlayerUpdateRetrieveView, \
    PlayerTransferPostView, TransferListView, TransferBuyPostView

urlpatterns = [
    path('teams/<int:team_id>/', TeamUpdateRetrieveView.as_view(), name='team_update_retrieve'),
    path('teams/<int:team_id>/players/', TeamPlayersListView.as_view(), name='team_list_players'),
    path('players/<int:player_id>/', PlayerUpdateRetrieveView.as_view(), name='player_update_retrieve'),
    path('players/<int:player_id>/transfer/', PlayerTransferPostView.as_view(), name='player_transfer_create'),
    path('market/', TransferListView.as_view(), name='pending_transfers_list'),
    path('market/<int:transfer_id>/buy/', TransferBuyPostView.as_view(), name='buy_player'),
]
