from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from lists.models import Item, List

class ItemModelTest(TestCase):

  def test_default_text(self):
    item = Item()
    self.assertEqual(item.text, '')

  def test_item_is_related_to_list(self):
    current_list = List.objects.create()
    item = Item()
    item.list = current_list
    item.save()
    self.assertIn(item, current_list.item_set.all())

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

  def test_duplicate_items_are_invalid(self):
    current_list = List.objects.create()
    Item.objects.create(list=current_list, text='bla')
    with self.assertRaises(ValidationError):
      duplicate = Item(list=current_list, text='bla')
      duplicate.full_clean()

  def test_can_save_item_to_different_lists(self):
    list1 = List.objects.create()
    list2 = List.objects.create()
    Item.objects.create(list=list1, text='bla')
    item2 = Item(list=list2, text='bla')
    try:
      item2.full_clean()
    except ValidationError:
      self.fail('Validation error')


class ListModelTest(TestCase):
  
  def test_get_absolute_url(self):
    current_list = List.objects.create()
    self.assertEqual(
      current_list.get_absolute_url(), 
      f'/lists/{current_list.id}/'
    )


