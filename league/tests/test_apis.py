import string
from decimal import Decimal
from random import randint, choices

from django.test import TestCase
from django.contrib.auth import get_user_model
from django_countries.fields import Country

from league.constants import TransferStatus
from league.models import Team, Player, Transfer
from league.services import generate_team_with_players

User = get_user_model()


class MyTeamRetrieveApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.team_url = f'/api/league/my_team/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        self.auth_header = f'Bearer {self.user.token}'

    def test_retrieve_my_team_non_authenticated(self) -> None:
        response = self.client.get(self.team_url)
        self.assertEqual(response.status_code, 401)

    def test_retrieve_my_team_authenticated_non_team_owner(self) -> None:
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_my_team_by_team_owner(self) -> None:
        generate_team_with_players(self.user)
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(self.user.is_team_owner)
        self.assertEqual(response_data['id'], self.user.team.id)
        self.assertEqual(response_data['name'], self.user.team.name)
        self.assertEqual(response_data['country'], self.user.team.country.name)
        self.assertEqual(Decimal(response_data['budget']), self.user.team.budget)
        self.assertEqual(Decimal(response_data['value']), self.user.team.value)


class ListTeamsApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.team_url = f'/api/league/teams/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        self.auth_header = f'Bearer {self.user.token}'

    def test_list_teams_non_authenticated(self) -> None:
        response = self.client.get(self.team_url)
        self.assertEqual(response.status_code, 401)

    def test_list_teams_authenticated(self) -> None:
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


class ListPlayersApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.team_url = f'/api/league/players/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        self.auth_header = f'Bearer {self.user.token}'

    def test_list_players_non_authenticated(self) -> None:
        response = self.client.get(self.team_url)
        self.assertEqual(response.status_code, 401)

    def test_list_players_authenticated(self) -> None:
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


class ListTeamPlayersApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        self.team = Team.objects.create(name='some random team', owner=self.user)
        self.team_url = f'/api/league/teams/{self.team.id}/players/'
        self.auth_header = f'Bearer {self.user.token}'

    def test_list_team_players_non_authenticated(self) -> None:
        response = self.client.get(self.team_url)
        self.assertEqual(response.status_code, 401)

    def test_list_team_players_authenticated(self) -> None:
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


class TeamUpdateRetrieveApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_url = f'/api/league/teams/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        generate_team_with_players(self.user)
        self.team = Team.objects.first()
        self.team_url = f'{self.base_url}{self.team.id}/'
        self.auth_header = f'Bearer {self.user.token}'

    def test_retrieve_team_authenticated(self) -> None:
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['id'], self.team.id)
        self.assertEqual(response_data['name'], self.team.name)
        self.assertEqual(response_data['country'], self.team.country.name)
        self.assertEqual(Decimal(response_data['budget']), self.team.budget)
        self.assertEqual(Decimal(response_data['value']), self.team.value)

    def test_retrieve_team_non_authenticated(self) -> None:
        response = self.client.get(self.team_url)
        self.assertEqual(response.status_code, 401)

    def test_retrieve_team_authenticated_non_team_owner(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'
        response = self.client.get(self.team_url, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 200)

    def test_update_team_owner(self) -> None:
        team_name = 'Manchester United'
        country_code = 'GB'
        if self.team.country.code.upper() == country_code:
            country_code = 'ESP'
        if self.team.name.upper() == team_name.upper():
            team_name = 'Barcelona FC'

        update_data = {
            "name": team_name,
            "country": country_code
        }
        response = self.client.patch(
            self.team_url,
            data=update_data,
            HTTP_AUTHORIZATION=self.auth_header,
            content_type='application/json'
            )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['id'], self.team.id)
        self.assertEqual(response_data['name'], team_name)
        self.assertEqual(response_data['country'], Country(code=country_code).name)

    def test_update_non_team_owner(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'

        update_data = {
            "name": 'not my team',
            "country": 'arg'
        }
        response = self.client.patch(
            self.team_url,
            data=update_data,
            HTTP_AUTHORIZATION=jwt_header,
            content_type='application/json'
            )

        self.assertEqual(response.status_code, 403)

    def test_update_non_authenticated(self) -> None:
        update_data = {
            "name": 'not my team',
            "country": 'arg'
        }
        response = self.client.patch(
            self.team_url,
            data=update_data,
            content_type='application/json'
            )

        self.assertEqual(response.status_code, 401)

    def test_update_name_uniqueness(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        other_team = Team.objects.create(owner=other_user, name='Just some team')
        team_update_url = f'{self.base_url}{other_team.id}/'
        jwt_header = f'Bearer {other_user.token}'
        update_data = {
            "name": self.team.name,
            "country": 'arg'
        }

        response = self.client.patch(
            team_update_url,
            data=update_data,
            HTTP_AUTHORIZATION=jwt_header,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)


class PlayerUpdateRetrieveApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_url = f'/api/league/players/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        generate_team_with_players(self.user)
        self.player = Player.objects.first()
        self.player_url = f'{self.base_url}{self.player.id}/'
        self.auth_header = f'Bearer {self.user.token}'

    def test_retrieve_player_authenticated(self) -> None:
        response = self.client.get(self.player_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['id'], self.player.id)
        self.assertEqual(response_data['first_name'], self.player.first_name)
        self.assertEqual(response_data['last_name'], self.player.last_name)
        self.assertEqual(response_data['country'], self.player.country.name)
        self.assertEqual(Decimal(response_data['age']), self.player.age)
        self.assertEqual(Decimal(response_data['value']), self.player.value)
        self.assertEqual(response_data['team'], self.player.team.id)
        self.assertEqual(response_data['team_name'], self.player.team.name)

    def test_retrieve_player_non_authenticated(self) -> None:
        response = self.client.get(self.player_url)
        self.assertEqual(response.status_code, 401)

    def test_retrieve_player_authenticated_non_team_owner(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'
        response = self.client.get(self.player_url, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 200)

    def test_update_player_by_team_owner(self) -> None:
        first_name = 'somefirstname'
        last_name = 'actuallastname'
        country_code = 'TZ'
        if self.player.country.code == country_code:
            country_code = 'ZIM'
        update_data = {
            "first_name": first_name,
            "last_name": last_name,
            "country": country_code
        }
        response = self.client.patch(
            self.player_url,
            data=update_data,
            HTTP_AUTHORIZATION=self.auth_header,
            content_type='application/json'
            )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['id'], self.player.id)
        self.assertEqual(response_data['first_name'], first_name)
        self.assertEqual(response_data['last_name'], last_name)
        self.assertEqual(response_data['country'], Country(code=country_code).name)

    def test_update_player_non_team_owner(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'

        update_data = {
            "first_name": "not my",
            "last_name": "player",
            "country": 'arg'
        }
        response = self.client.patch(
            self.player_url,
            data=update_data,
            HTTP_AUTHORIZATION=jwt_header,
            content_type='application/json'
            )
        self.assertEqual(response.status_code, 403)

    def test_update_non_authenticated(self) -> None:
        update_data = {
            "first_name": "other",
            "last_name": "player",
            "country": "arg"
        }
        response = self.client.put(
            self.player_url,
            data=update_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)


class PlayerTransferApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_url = f'/api/league/players/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        generate_team_with_players(self.user)
        self.player = Player.objects.first()
        self.player_transfer_url = f'{self.base_url}{self.player.id}/transfer/'
        self.auth_header = f'Bearer {self.user.token}'

    def test_player_transfer_non_authenticated_user(self) -> None:
        price = randint(100000, 3000000)
        transfer_data = {"price": price}
        response = self.client.post(self.player_transfer_url, data=transfer_data)
        self.assertEqual(response.status_code, 401)

    def test_player_transfer_non_team_owner(self) -> None:
        price = randint(100000, 3000000)
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'
        transfer_data = {"price": price}
        response = self.client.post(self.player_transfer_url, data=transfer_data, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 403)

    def test_player_transfer_team_owner(self) -> None:
        price = randint(100000, 3000000)
        transfer_data = {"price": price}
        response = self.client.post(self.player_transfer_url, data=transfer_data, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(Decimal(response_data['price']), Decimal(price))
        self.assertEqual(response_data['status'], TransferStatus.PENDING)
        self.assertEqual(response_data['player'], self.player.id)
        self.assertEqual(response_data['seller'], self.user.team.id)
        self.assertEqual(response_data['seller_name'], self.user.team.name)

    def test_player_transfer_with_pending_transfer(self) -> None:
        price = randint(100000, 3000000)
        Transfer.objects.create(player=self.player, price=price)
        transfer_data = {'price': randint(100000, 3000000)}
        response = self.client.post(self.player_transfer_url, data=transfer_data, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_non_existing_player_transfer(self) -> None:
        last_player = Player.objects.last()
        player_id = last_player.id if last_player else 0
        player_id += randint(10, 100)
        transfer_url = f'{self.base_url}{player_id}/transfer/'
        transfer_data = {'price': randint(100000, 3000000)}
        response = self.client.post(transfer_url, data=transfer_data, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 404)


class ListPendingTransfersApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        self.market_url = f'/api/league/market/'
        self.auth_header = f'Bearer {self.user.token}'

    def test_list_pending_transfers_non_authenticated(self) -> None:
        response = self.client.get(self.market_url)
        self.assertEqual(response.status_code, 401)

    def test_list_pending_transfers_authenticated(self) -> None:
        response = self.client.get(self.market_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


class TransferRetrieveByPlayerIDApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        self.team = Team.objects.create(owner=self.user, name='test team name')
        self.player = Player.objects.create(team=self.team, first_name='first', last_name='last', age=22)
        self.transfer_url = f'/api/league/market/{self.player.id}/'
        self.auth_header = f'Bearer {self.user.token}'

    def test_retrieve_transfer_by_player_non_authenticated(self) -> None:
        response = self.client.get(self.transfer_url)
        self.assertEqual(response.status_code, 401)

    def test_retrieve_non_active_transfer_by_player_authenticated_non_team_owner(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'
        response = self.client.get(self.transfer_url, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_non_active_transfer_by_player_by_team_owner(self) -> None:
        response = self.client.get(self.transfer_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_pending_transfer_by_player_by_team_owner(self) -> None:
        transfer = Transfer.objects.create(player=self.player, seller=self.team, price=2000000)
        response = self.client.get(self.transfer_url, HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(self.user.is_team_owner)
        self.assertEqual(response_data['player'], self.player.id)
        self.assertEqual(response_data['first_name'], self.player.first_name)
        self.assertEqual(response_data['last_name'], self.player.last_name)
        self.assertEqual(response_data['team'], self.team.id)
        self.assertEqual(response_data['team_name'], self.team.name)
        self.assertEqual(response_data['status'], TransferStatus.PENDING)
        self.assertEqual(Decimal(response_data['current_value']), self.player.value)
        self.assertEqual(Decimal(response_data['price']), transfer.price)


class PlayerBuyApiTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.base_url = f'/api/league/players/'
        self.user = User.objects.create_user(
            email='johndoe@onlinesoccermanager.com',
            first_name='John',
            last_name='Doe',
            password='barbarfoo'
        )
        generate_team_with_players(self.user)
        self.player = Player.objects.first()
        price = randint(100000,2000000)
        self.transfer = Transfer.objects.create(player=self.player, price=price)
        self.player_buy_url = f'{self.base_url}{self.player.id}/buy/'

    def test_player_buy_unauthenticated_user(self) -> None:
        response = self.client.post(self.player_buy_url)
        self.assertEqual(response.status_code, 401)

    def test_player_buy_by_seller(self) -> None:
        jwt_header = f'Bearer {self.user.token}'
        response = self.client.post(self.player_buy_url, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 403)

    def test_player_buy_user_without_team(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        jwt_header = f'Bearer {other_user.token}'
        response = self.client.post(self.player_buy_url, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 403)

    def test_player_buy_user_with_team(self) -> None:
        other_user = User.objects.create_user(
            email='notme@onlinesoccermanager.com',
            first_name='Not',
            last_name='Me',
            password='barbarfoo'
        )
        seller = self.transfer.seller
        old_player_value = self.player.value
        team_name = ''.join(choices(string.ascii_lowercase + string.digits, k=15))
        buyer = Team.objects.create(owner=other_user, name=team_name)
        old_buyer_team_budget = buyer.budget
        old_seller_team_budget = seller.budget
        jwt_header = f'Bearer {other_user.token}'
        response = self.client.post(self.player_buy_url, HTTP_AUTHORIZATION=jwt_header)
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.player.refresh_from_db()
        self.assertEqual(response_data['id'], self.player.id)
        self.assertEqual(response_data['team'], buyer.id)
        self.assertGreater(self.player.value, old_player_value)
        self.assertNotIn(self.player, self.user.team.players.all())
        seller.refresh_from_db()
        buyer.refresh_from_db()
        self.assertEqual(seller.budget, old_seller_team_budget + self.transfer.price)
        self.assertEqual(buyer.budget, old_buyer_team_budget - self.transfer.price)
        self.assertIn(self.player, other_user.team.players.all())
