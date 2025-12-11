from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
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

  def test_cannot_save_null_list_items(self):
    new_list = List.objects.create()
    new_item = Item(list=new_list, text=None)

    with self.assertRaises(IntegrityError):
      new_item.save()

  def test_cannot_save_emtpy_list_items(self):
    new_list = List.objects.create()
    new_item = Item(list=new_list, text='')

    with self.assertRaises(ValidationError):
      new_item.full_clean()

  def test_get_absolute_url(self):
    current_list = List.objects.create()
    self.assertEqual(
      current_list.get_absolute_url(), 
      f'/lists/{current_list.id}/'
    )

