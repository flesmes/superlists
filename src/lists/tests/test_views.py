from django.test import TestCase
from django.utils import html
import lxml.html
from unittest import skip

from lists.forms import DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR
from lists.models import Item, List

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
      'text', 
      [input.get('name') for input in form.cssselect('input')]
    )
 

class ListViewTest(TestCase):

  def post_empty_item(self):
    current_list = List.objects.create()
    return self.client.post(f'/lists/{current_list.id}/', data={'text': ''})

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
    self.assertEqual(form.get('action'), f'/lists/{mylist.id}/')

    self.assertIn(
      'text', 
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


  def test_can_save_a_POST_request_to_an_existing_list(self):
    List.objects.create()
    correct_list = List.objects.create()
    self.client.post(
      f'/lists/{correct_list.id}/', 
      data={'text': 'New item text'}
    )

    self.assertEqual(Item.objects.count(), 1)
    new_item = Item.objects.get()

    self.assertEqual(new_item.text, 'New item text')
    self.assertEqual(new_item.list, correct_list)


  def test_POST_redirects_to_list_view(self):
    List.objects.create()
    correct_list = List.objects.create()

    response = self.client.post(
      f'/lists/{correct_list.id}/', 
      data={'text': 'New item text'}
    )

    self.assertRedirects(response, f'/lists/{correct_list.id}/')

  def test_for_empty_item_nothing_saved_to_db(self):
    self.post_empty_item()
    self.assertEqual(Item.objects.count(), 0)

  def test_for_empty_item_renders_list_template(self):
    response = self.post_empty_item()
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'list.html')

  def test_for_empty_item_shows_error_on_page(self):
    response = self.post_empty_item()
    self.assertContains(response, html.escape(EMPTY_ITEM_ERROR))

  def test_for_empty_item_sets_is_invalid_class(self):
    response = self.post_empty_item()
    parsed = lxml.html.fromstring(response.content)
    inputs = parsed.cssselect('input[name=text]')
    self.assertEqual(len(inputs), 1)
    self.assertIn('is-invalid', set(inputs[0].classes))

  def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
    list1 = List.objects.create()
    Item.objects.create(list=list1, text='textey')

    response = self.client.post(
      f'/lists/{list1.id}/',
      data={'text': 'textey'}
    )

    expected_error = html.escape(DUPLICATE_ITEM_ERROR)
    self.assertContains(response, expected_error)
    self.assertTemplateUsed(response, 'list.html')
    self.assertEqual(Item.objects.count(), 1)


class NewListTest(TestCase):

  def post_emtpy_item(self):
    return self.client.post('/lists/new', data={'text': ''})

  def test_can_save_a_POST_request(self):
    text = 'A new list item'
    self.client.post('/lists/new', data={'text': text})

    new_item = Item.objects.first()

    self.assertEqual(Item.objects.count(), 1)
    self.assertEqual(new_item.text, text)

  def test_redirects_after_POST(self):
    response = self.client.post(
      '/lists/new', 
      data={'text': 'New list item'}
    )
    new_list = List.objects.get()
    self.assertRedirects(response, f'/lists/{new_list.id}/')

  def test_for_empty_item_nothing_saved_to_db(self):
    self.post_emtpy_item()
    self.assertEqual(Item.objects.count(), 0)

  def test_for_empty_item_renders_list_template(self):
    response = self.post_emtpy_item()
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'home.html')

  def test_for_empty_item_shows_error_on_page(self):
    response = self.post_emtpy_item()
    self.assertContains(response, html.escape(EMPTY_ITEM_ERROR))

