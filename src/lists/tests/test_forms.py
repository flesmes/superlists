from django.test import TestCase

from lists.forms import (
  DUPLICATE_ITEM_ERROR, 
  EMPTY_ITEM_ERROR, 
  ExistingListItemForm,
  ItemForm
)
from lists.models import Item, List

class ItemFormTest(TestCase):

  def test_form_validation_for_black_items(self):
    form = ItemForm(data={'text': ''})
    self.assertFalse(form.is_valid())
    self.assertEqual(
      form.errors['text'], 
      [EMPTY_ITEM_ERROR]
    )

  def test_form_save_handles_saving_to_a_list(self):
    current_list = List.objects.create()
    form = ItemForm(data={'text': 'do me'})
    form.is_valid()
    new_item = form.save(for_list=current_list)
    self.assertEqual(new_item, Item.objects.get())
    self.assertEqual(new_item.text, 'do me')
    self.assertEqual(new_item.list, current_list)


class ExistingListItemFormTest(TestCase):

  def test_form_validation_for_blank_items(self):
    list1 = List.objects.create()
    form = ExistingListItemForm(for_list=list1, data={'text': ''})
    self.assertFalse(form.is_valid())
    self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

  def test_form_validation_for_duplicate_items(self):
    list1 = List.objects.create()
    Item.objects.create(list=list1, text='no twins')
    form = ExistingListItemForm(for_list=list1, data={'text': 'no twins'})
    self.assertFalse(form.is_valid())
    self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])

  def test_form_save(self):
    current_list = List.objects.create()
    form = ExistingListItemForm(for_list=current_list, data={'text': 'hi'})
    self.assertTrue(form.is_valid())
    new_item = form.save()
    self.assertEqual(new_item, Item.objects.get())
