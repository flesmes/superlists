from django.test import TestCase
from lists.models import Item, List
import lxml.html

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
    parsed = lxml.html.fromstring(response.content)

    forms = parsed.cssselect('form[method=POST]')
    self.assertEqual(len(forms), 1)
    form = forms[0]
    self.assertEqual(form.get('action'), '/lists/new')

    self.assertIn(
      'item_text', 
      [input.get('name') for input in form.cssselect('input')]
    )
 

class ListViewTest(TestCase):

  def test_uses_list_template(self):
    mylist = List.objects.create()
    response = self.client.get(f'/lists/{mylist.id}/')
    self.assertTemplateUsed(response, 'list.html')

  def test_renders_input_form(self):
    mylist = List.objects.create()
    response = self.client.get(f'/lists/{mylist.id}/')
    parsed = lxml.html.fromstring(response.content)

    forms = parsed.cssselect('form[method=POST]')
    self.assertEqual(len(forms), 1)
    form = forms[0]
    self.assertEqual(form.get('action'), f'/lists/{mylist.id}/add_item')

    self.assertIn(
      'item_text', 
      [input.get('name') for input in form.cssselect('input')]
    )

  def test_display_only_items_for_that_list(self):
    correct_list = List.objects.create()
    other_list = List.objects.create()
    Item.objects.create(text='Item 1', list=correct_list)
    Item.objects.create(text='Item 2', list=correct_list)
    Item.objects.create(text='Other list item', list=other_list)

    response = self.client.get(f'/lists/{correct_list.id}/')
    
    self.assertContains(response, 'Item 1')
    self.assertContains(response, 'Item 2')
    self.assertNotContains(response, 'Other list item')

class NewListTest(TestCase):

  def test_can_save_a_POST_request(self):
    text = 'A new list item'
    self.client.post('/lists/new', data={'item_text': text})

    new_item = Item.objects.first()

    self.assertEqual(Item.objects.count(), 1)
    self.assertEqual(new_item.text, text)

  def test_redirects_after_POST(self):
    response = self.client.post(
      '/lists/new', 
      data={'item_text': 'New list item'}
    )
    new_list = List.objects.get()
    self.assertRedirects(response, f'/lists/{new_list.id}/')

class NewItemTest(TestCase):

  def test_can_save_a_POST_request_to_an_existing_list(self):
    new_list = List.objects.create()
    self.client.post(
      f'/lists/{new_list.id}/add_item', 
      data={'item_text': 'New item text'}
    )

    new_item = Item.objects.get(id=new_list.id)

    self.assertEqual(Item.objects.count(), 1)
    self.assertEqual(new_item.text, 'New item text')
    self.assertEqual(new_item.list, new_list)

  def test_redirects_to_list_view(self):
    new_list = List.objects.create()

    response = self.client.post(
      f'/lists/{new_list.id}/add_item', 
      data={'item_text': 'New item text'}
    )

    self.assertRedirects(response, f'/lists/{new_list.id}/')
