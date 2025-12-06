from django.test import TestCase
from lists.models import Item

class ItemModelTest(TestCase):

  def test_saving_and_retrieving_items(self):
    first_item = Item()
    first_item.text = 'The first list item'
    first_item.save()

    second_item = Item()
    second_item.text = 'Item the second'
    second_item.save()

    saved_items = Item.objects.all().order_by('id')
    self.assertEqual(saved_items.count(), 2)

    first_saved_item = saved_items[0]
    second_saved_item = saved_items[1]
    self.assertEqual(first_saved_item.text, 'The first list item')
    self.assertEqual(second_saved_item.text, 'Item the second')


class HomePageTest(TestCase):

  def test_uses_home_template(self):
    response = self.client.get('/')
    self.assertTemplateUsed(response, 'home.html')

  def test_renders_input_form(self):
    response = self.client.get('/')
    self.assertContains(
      response, 
      '<form method="POST" action="/lists/new">'
    )
    self.assertContains(response, '<input name="item_text"')

class NewListTest(TestCase):

  def test_can_save_a_POST_request(self):
    text = 'A new list item'
    response = self.client.post('/lists/new', data={'item_text': text})
    new_item = Item.objects.first()

    self.assertEqual(Item.objects.count(), 1)
    self.assertEqual(new_item.text, text)

  def test_redirects_after_POST(self):
    response = self.client.post(
      '/lists/new', 
      data={'item_text': 'New list item'}
    )
    self.assertRedirects(response, '/lists/single/')


class ListViewTest(TestCase):

  def test_uses_list_template(self):
    response = self.client.get('/lists/single/')
    self.assertTemplateUsed(response, 'list.html')

  def test_renders_input_form(self):
    response = self.client.get('/lists/single/')
    self.assertContains(
      response, 
      '<form method="POST" action="/lists/new">'
    )
    self.assertContains(response, '<input name="item_text"')

  def test_display_all_list_items(self):
    Item.objects.create(text='Item 1')
    Item.objects.create(text='Item 2')

    response = self.client.get('/lists/single/')
    
    self.assertContains(response, 'Item 1')
    self.assertContains(response, 'Item 2')

