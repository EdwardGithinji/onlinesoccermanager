from django.test import TestCase
from django.contrib.auth import get_user_model

from league.constants import PlayerPosition

User = get_user_model()


class UsersApiTestCase(TestCase):

    def test_register_user(self):
        register_url = '/api/auth/registration/'
        email = 'mary_sue@onlinesoccermanager.com'
        register_data = dict(
            email=email,
            password1='1326a12vr',
            password2='1326a12vr'
        )
        response = self.client.post(register_url, data=register_data)
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data['email'], email)
        user = User.objects.get(id=response_data['id'])
        self.assertTrue(user.is_team_owner)
        players = user.team.players
        self.assertEqual(players.count(), 20)
        self.assertEqual(players.filter(position=PlayerPosition.GOALKEEPER).count(), 3)
        self.assertEqual(players.filter(position=PlayerPosition.DEFENDER).count(), 6)
        self.assertEqual(players.filter(position=PlayerPosition.MIDFIELDER).count(), 6)
        self.assertEqual(players.filter(position=PlayerPosition.ATTACKER).count(), 5)

    def test_register_user_non_matching_passwords(self):
        register_url = '/api/auth/registration/'
        email = 'jane_doe@onlinesoccermanager.com'
        register_data = dict(
            email=email,
            password1='1326a12vr',
            password2='foobarfoo'
        )
        response = self.client.post(register_url, data=register_data)
        self.assertEqual(response.status_code, 400)

    def test_register_user_short_password(self):
        register_url = '/api/auth/registration/'
        email = 'jane_doe@onlinesoccermanager.com'
        register_data = dict(
            email=email,
            password1='foo',
            password2='foo'
        )
        response = self.client.post(register_url, data=register_data)
        self.assertEqual(response.status_code, 400)

    def test_user_login(self):
        login_url = '/api/auth/login/'
        email = 'john_doe@onlinesoccermanager.com'
        user: User = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email=email,
            password='foobarfoo'
        )
        login_data = dict(email=email, password='foobarfoo')
        response = self.client.post(login_url, data=login_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

        login_data = dict(email=email, password='foobar')
        response = self.client.post(login_url, data=login_data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
