from unittest import mock

from django.test import TestCase
from django.urls import reverse

import accounts.views

class SendLoginEmailViewTest(TestCase):

  def test_redirects_to_home_page(self):
    response = self.client.post(
      reverse('send_login_email'), 
      data={'email': 'name@example.com'}
    )
    self.assertRedirects(response, reverse('home')) 

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