from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django_countries.serializer_fields import CountryField
from league.constants import PlayerPosition

from league.selectors import team_retrieve, team_list_players, player_retrieve, \
    active_transfers_list, user_team_retrieve, team_list, players_list
from league.services import team_update, player_update, player_transfer_create, \
    player_buy
from onlinesoccermanager.pagination import LinkHeaderPagination


class MyTeamRetrieveView(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        country = CountryField(name_only=True)
        budget = serializers.DecimalField(max_digits=65, decimal_places=2)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)

    def get(self, request):
        team = user_team_retrieve(request.user)
        response_data = self.OutputSerializer(team).data
        return Response(response_data, status=status.HTTP_200_OK)


class TeamListView(APIView, LinkHeaderPagination):
    class FilterSerializer(serializers.Serializer):
        country = CountryField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        country = CountryField(name_only=True)
        # budget = serializers.DecimalField(max_digits=65, decimal_places=2)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        teams = team_list(filters=filter_serializer.validated_data)
        page = self.paginate_queryset(teams, request, view=self)
        if page is not None:
            response_data = self.OutputSerializer(page, many=True).data
            return self.get_paginated_response(response_data)
        response_data = self.OutputSerializer(teams, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


class TeamUpdateRetrieveView(APIView):

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, allow_null=False)
        country = CountryField(required=False, allow_null=False)

    class OutputSerializer(serializers.Serializer):
        class OwnerSerializer(serializers.Serializer):
            # id = serializers.IntegerField()
            # email = serializers.EmailField()
            first_name = serializers.CharField()
            last_name = serializers.CharField()

        id = serializers.IntegerField()
        name = serializers.CharField()
        country = CountryField(name_only=True)
        budget = serializers.DecimalField(max_digits=65, decimal_places=2)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)
        owner = OwnerSerializer()

    def get(self, request, team_id):
        team = team_retrieve(team_id)
        response_data = self.OutputSerializer(team).data
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, team_id):
        team = team_retrieve(team_id)
        team_update_serializer = self.InputSerializer(data=request.data)
        team_update_serializer.is_valid(raise_exception=True)
        team = team_update(**team_update_serializer.validated_data, team=team, user=request.user)
        response_data = self.OutputSerializer(team).data
        return Response(response_data, status=status.HTTP_200_OK)


class TeamPlayersListView(APIView, LinkHeaderPagination):

    class FilterSerializer(serializers.Serializer):
        position = serializers.ChoiceField(choices=PlayerPosition.choices, required=False)
        country = CountryField(required=False)
        sort_by = serializers.ChoiceField(choices=('age', '-age', 'value', '-value'), required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        age = serializers.IntegerField()
        position = serializers.CharField()
        country = CountryField(name_only=True)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)
        team = serializers.IntegerField(source='team.id')


    def get(self, request, team_id):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        players = team_list_players(team_id, filters=filter_serializer.validated_data)
        page = self.paginate_queryset(players, request, view=self)
        if page is not None:
            response_data = self.OutputSerializer(page, many=True).data
            return self.get_paginated_response(response_data)
        response_data = self.OutputSerializer(players, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


class PlayerListView(APIView, LinkHeaderPagination):
    class FilterSerializer(serializers.Serializer):
        team = serializers.IntegerField(required=False)
        country = CountryField(required=False)
        sort_by = serializers.ChoiceField(choices=('age', '-age', 'value', '-value'), required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        age = serializers.IntegerField()
        position = serializers.CharField()
        country = CountryField(name_only=True)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)
        team = serializers.IntegerField(source='team.id')

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        players = players_list(filters=filter_serializer.validated_data)
        page = self.paginate_queryset(players, request, view=self)
        if page is not None:
            response_data = self.OutputSerializer(page, many=True).data
            return self.get_paginated_response(response_data)
        response_data = self.OutputSerializer(players, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


class PlayerUpdateRetrieveView(APIView):

    class InputSerializer(serializers.Serializer):
        first_name = serializers.CharField(required=False, allow_null=False)
        last_name = serializers.CharField(required=False, allow_null=False)
        country = CountryField(required=False, allow_null=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        age = serializers.IntegerField()
        position = serializers.CharField()
        country = CountryField(name_only=True)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)
        team = serializers.IntegerField(source='team.id')
        team_name = serializers.CharField(source='team.name')

    def get(self, request, player_id):
        player = player_retrieve(player_id)
        response_data = self.OutputSerializer(player).data
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, player_id):
        player = player_retrieve(player_id)
        player_update_serializer = self.InputSerializer(data=request.data)
        player_update_serializer.is_valid(raise_exception=True)
        player = player_update(**player_update_serializer.validated_data, player=player, user=request.user)
        response_data = self.OutputSerializer(player).data
        return Response(response_data, status=status.HTTP_200_OK)


class TransferListView(APIView, LinkHeaderPagination):

    class FilterSerializer(serializers.Serializer):
        position = serializers.ChoiceField(choices=PlayerPosition.choices, required=False)
        player = serializers.IntegerField(required=False)
        seller = serializers.IntegerField(required=False)
        sort_by = serializers.ChoiceField(choices=('price', '-price'), required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        player = serializers.IntegerField(source='player.id')
        first_name = serializers.CharField(source='player.first_name')
        last_name = serializers.CharField(source='player.last_name')
        position = serializers.CharField(source='player.position')
        seller = serializers.IntegerField(source='seller.id')
        seller_name = serializers.CharField(source='seller.name')
        price = serializers.DecimalField(max_digits=65, decimal_places=2)
        status = serializers.CharField()

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        transfers = active_transfers_list(filters=filter_serializer.validated_data)
        page = self.paginate_queryset(transfers, request, view=self)
        if page is not None:
            response_data = self.OutputSerializer(page, many=True).data
            return self.get_paginated_response(response_data)
        response_data = self.OutputSerializer(transfers, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


class PlayerTransferPostView(APIView):

    class InputSerializer(serializers.Serializer):
        price = serializers.DecimalField(max_digits=65, decimal_places=2, min_value=1)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        player = serializers.IntegerField(source='player.id')
        first_name = serializers.CharField(source='player.first_name')
        last_name = serializers.CharField(source='player.last_name')
        position = serializers.CharField(source='player.position')
        seller = serializers.IntegerField(source='seller.id')
        seller_name = serializers.CharField(source='seller.name')
        price = serializers.DecimalField(max_digits=65, decimal_places=2)
        status = serializers.CharField()

    def post(self, request, player_id):
        player_transfer_create_serializer = self.InputSerializer(data=request.data)
        player_transfer_create_serializer.is_valid(raise_exception=True)
        transfer = player_transfer_create(
            **player_transfer_create_serializer.validated_data,
            player_id=player_id,
            user=request.user
            )
        response_data = self.OutputSerializer(transfer).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class PlayerBuyView(APIView):

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        age = serializers.IntegerField()
        position = serializers.CharField()
        country = CountryField(name_only=True)
        value = serializers.DecimalField(max_digits=65, decimal_places=2)
        team = serializers.IntegerField(source='team.id')
        team_name = serializers.CharField(source='team.name')

    def post(self, request, player_id):
        player = player_buy(player_id, user=request.user)
        response_data = self.OutputSerializer(player).data
        return Response(response_data, status=status.HTTP_201_CREATED)


# class TransferBuyPostView(APIView):

#     class OutputSerializer(serializers.Serializer):
#         id = serializers.IntegerField()
#         player = serializers.IntegerField(source='player.id')
#         player_first_name = serializers.CharField(source='player.first_name')
#         player_last_name = serializers.CharField(source='player.last_name')
#         seller = serializers.IntegerField(source='seller.id')
#         seller_name = serializers.CharField(source='seller.name')
#         price = serializers.DecimalField(max_digits=65, decimal_places=2)
#         status = serializers.CharField()
#         buyer = serializers.IntegerField(source='buyer.id')
#         buyer_name = serializers.CharField(source='buyer.name')

#     def post(self, request, transfer_id):
#         transfer = buy_player_complete_transfer(transfer_id, user=request.user)
#         response_data = self.OutputSerializer(transfer).data
#         return Response(response_data, status=status.HTTP_201_CREATED)
