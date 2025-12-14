from django.contrib import auth
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User

class UserModelTest(TestCase):

  def test_model_is_configured_for_django_auth(self):
    self.assertEqual(auth.get_user_model(), User)

  def test_user_is_valid_with_email_only(self):
    user = User(email='name@example.com')
    try:
      user.full_clean()
    except ValidationError:
      self.fail('User not valid')

  def test_email_is_primary_key(self):
    user = User(email='name@example.com')
    self.assertEqual(user.pk, 'name@example.com')