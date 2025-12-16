from unittest import mock

from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from accounts.models import Token

class SendLoginEmailViewTest(TestCase):

  def test_redirects_to_home_page(self):
    response = self.client.post(
      reverse('send_login_email'), 
      data={'email': 'name@example.com'}
    )
    self.assertRedirects(response, reverse('home')) 

  def test_adds_success_message(self):
    response = self.client.post(
      reverse('send_login_email'),
      data={'email': 'edith@example.com'},
      follow=True
    )

    message = next(iter(response.context['messages']))
    self.assertEqual(
      message.message,
      'Check your email, we\'ve sent you a link you can use to log in.'
    )
    self.assertEqual(message.tags, 'success')

  @mock.patch('accounts.views.send_mail')
  def test_sends_mail_to_address_from_post(self, mock_send_mail):
    self.client.post(
      reverse('send_login_email'), 
      data={'email': 'edith@example.com'}
    )

    self.assertTrue(mock_send_mail.called)
    (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
    self.assertEqual(subject, 'Your login link for Superlists')
    self.assertEqual(from_email, 'noreply@flesmes.com')
    self.assertEqual(to_list, ['edith@example.com'])

  def test_creates_token_associated_with_email(self):
    self.client.post(
      reverse('send_login_email'), 
      data={'email': 'edith@example.com'}
    )
    token = Token.objects.get()
    self.assertEqual(token.email, 'edith@example.com')

  @mock.patch('accounts.views.send_mail')
  def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
    self.client.post(
      reverse('send_login_email'), 
      data={'email': 'edith@example.com'}
    )
    token = Token.objects.get()
    expected_url = f'http://testserver/accounts/login?token={token.uid}'
    (_, body, _, _), _ = mock_send_mail.call_args
    self.assertIn(expected_url, body)

class LoginViewTest(TestCase):

  def test_redirects_to_home_page(self):
    response = self.client.get(reverse('login', query={'token': 'abcd123'}))
    self.assertRedirects(response, reverse('home'))

  def test_logs_in_if_given_valid_token(self):
    anon_user = auth.get_user(self.client)
    self.assertFalse(anon_user.is_authenticated)

    token = Token.objects.create(email='edith@example.com')
    self.client.get(reverse('login', query={'token': token.uid}))

    user = auth.get_user(self.client)
    self.assertTrue(user.is_authenticated)
    self.assertEqual(user.email, 'edith@example.com')

  def test_shows_login_error_if_token_invalid(self):
    response = self.client.get(
      reverse('login', query={'token': 'invalid'}),
      follow=True
    )

    user = auth.get_user(self.client)
    self.assertFalse(user.is_authenticated)
    message, *rest = response.context['messages']
    self.assertEqual(
      message.message,
      'Invalid login link, please request a new one'
    )
    self.assertEqual(message.tags, 'error')

  @mock.patch('accounts.views.auth')
  def test_calls_django_auth_authenticate(self, mock_auth):
    self.client.get(reverse('login', query={'token': 'abcd123'}))
    self.assertEqual(
      mock_auth.authenticate.call_args,
      mock.call(uid='abcd123')
    )

