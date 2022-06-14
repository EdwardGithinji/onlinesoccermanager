from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_countries.serializer_fields import CountryField

from league.selectors import team_retrieve, team_list_players, player_retrieve, transfers_list
from league.services import team_update, player_update, player_transfer_create, buy_player_complete_transfer


class TeamUpdateRetrieveView(APIView):

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, allow_null=False)
        country = CountryField(required=False, allow_null=False)

    class OutputSerializer(serializers.Serializer):
        class OwnerSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            email = serializers.EmailField()
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


class TeamPlayersListView(APIView):

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
        players = team_list_players(team_id)
        response_data = self.OutputSerializer(players, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


class PlayerUpdateRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
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



class TransferListView(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        player = serializers.IntegerField(source='player.id')
        player_first_name = serializers.CharField(source='player.first_name')
        player_last_name = serializers.CharField(source='player.last_name')
        seller = serializers.IntegerField(source='seller.id')
        seller_name = serializers.CharField(source='seller.name')
        price = serializers.DecimalField(max_digits=65, decimal_places=2)
        status = serializers.CharField()

    def get(self, request):
        transfers = transfers_list()
        response_data = self.OutputSerializer(transfers, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)


class PlayerTransferPostView(APIView):

    class InputSerializer(serializers.Serializer):
        price = serializers.DecimalField(max_digits=65, decimal_places=2, min_value=1)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        player = serializers.IntegerField(source='player.id')
        player_first_name = serializers.CharField(source='player.first_name')
        player_last_name = serializers.CharField(source='player.last_name')
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


class TransferBuyPostView(APIView):

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        player = serializers.IntegerField(source='player.id')
        player_first_name = serializers.CharField(source='player.first_name')
        player_last_name = serializers.CharField(source='player.last_name')
        seller = serializers.IntegerField(source='seller.id')
        seller_name = serializers.CharField(source='seller.name')
        price = serializers.DecimalField(max_digits=65, decimal_places=2)
        status = serializers.CharField()
        buyer = serializers.IntegerField(source='buyer.id')
        buyer_name = serializers.CharField(source='buyer.name')

    def post(self, request, transfer_id):
        transfer = buy_player_complete_transfer(transfer_id, user=request.user)
        response_data = self.OutputSerializer(transfer).data
        return Response(response_data, status=status.HTTP_201_CREATED)
