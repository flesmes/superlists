from django.test import TestCase

class HomePageTest(TestCase):

  def test_uses_home_template(self):
    response = self.client.get('/')
    self.assertTemplateUsed(response, 'home.html')

  def test_renders_input_form(self):
    response = self.client.get('/')
    self.assertContains(response, '<form method="POST">')
    self.assertContains(response, '<input name="item_text"')

  def test_can_save_a_POST_request(self):
    text = 'A new list item'
    response = self.client.post('/', data={'item_text': text})
    self.assertContains(response, text)
    self.assertTemplateUsed(response, 'home.html')
