from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):

    def test_create_user(self) -> None:
        user: User = User.objects.create_user(
            first_name='Jane',
            last_name='Doe',
            email='jane_doe@onlinesoccermanager.com',
            password='foobarbar'
        )
        self.assertIn(user, User.objects.all())
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'jane_doe@onlinesoccermanager.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self) -> None:
        user: User = User.objects.create_superuser(
            first_name='Jane',
            last_name='Doe',
            email='jane_doe@onlinesoccermanager.com',
            password='foobarbar'
        )
        self.assertIn(user, User.objects.all())
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'jane_doe@onlinesoccermanager.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
