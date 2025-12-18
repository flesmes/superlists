from django.urls import reverse
from django.test import TestCase
from django.utils import html
import lxml.html
from unittest import skip

from accounts.models import User
from lists.forms import DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR
from lists.models import Item, List

class HomePageTest(TestCase):

  def test_uses_home_template(self):
    response = self.client.get('/')
    self.assertTemplateUsed(response, 'home.html')

  def test_renders_input_form(self):
    response = self.client.get('/')
    parsed = lxml.html.fromstring(response.content)

    new_list_forms = [form 
      for form in parsed.cssselect('form[method=POST]') 
      if form.get('action') == '/lists/new'
    ]
    self.assertEqual(len(new_list_forms), 1)
    form = new_list_forms[0]

    self.assertIn(
      'text', 
      [input.get('name') for input in form.cssselect('input')]
    )

class MyListTest(TestCase):

  def test_my_lists_url_renders_my_lists_template(self):
    User.objects.create(email='a@b.com')
    response = self.client.get(reverse('my_lists', args=('a@b.com',)))
    self.assertTemplateUsed(response, 'my_lists.html')

  def test_passes_correct_owner_to_template(self):
    User.objects.create(email='wrong@owner.com')
    correct_user = User.objects.create(email='a@b.com')
    response = self.client.get(reverse('my_lists', args=('a@b.com',)))
    self.assertEqual(response.context['owner'], correct_user)
 

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
    url = f'/lists/{mylist.id}/'
    response = self.client.get(url)
    parsed = lxml.html.fromstring(response.content)

    new_item_forms = [form 
      for form in parsed.cssselect('form[method=POST]') 
      if form.get('action') == url
    ]
    self.assertEqual(len(new_item_forms), 1)
    form = new_item_forms[0]

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

  def test_list_owner_is_saved_if_user_is_authenticated(self):
    user = User.objects.create(email='a@b.com')
    self.client.force_login(user)
    self.client.post('/lists/new', data={'text': 'new item'})
    new_list = List.objects.get()
    self.assertEqual(new_list.owner, user)



