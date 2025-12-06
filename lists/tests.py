from django.test import TestCase
from lists.models import Item, List

class ListAndItemModelTest(TestCase):

  def test_saving_and_retrieving_items(self):
    mylist = List()
    mylist.save()

    first_item = Item()
    first_item.text = 'The first list item'
    first_item.list = mylist
    first_item.save()

    second_item = Item()
    second_item.text = 'Item the second'
    second_item.list = mylist
    second_item.save()

    saved_list = List.objects.get()
    self.assertEqual(saved_list, mylist)

    saved_items = Item.objects.all().order_by('id')
    self.assertEqual(saved_items.count(), 2)

    first_saved_item = saved_items[0]
    second_saved_item = saved_items[1]
    self.assertEqual(first_saved_item.text, 'The first list item')
    self.assertEqual(first_saved_item.list, mylist)
    self.assertEqual(second_saved_item.text, 'Item the second')
    self.assertEqual(second_saved_item.list, mylist)


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
    mylist = List.objects.create()
    Item.objects.create(text='Item 1', list=mylist)
    Item.objects.create(text='Item 2', list=mylist)

    response = self.client.get('/lists/single/')
    
    self.assertContains(response, 'Item 1')
    self.assertContains(response, 'Item 2')

