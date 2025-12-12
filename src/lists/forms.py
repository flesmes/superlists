from django import forms

from lists.models import Item

DUPLICATE_ITEM_ERROR = 'You\'ve already got this in your list'
EMPTY_ITEM_ERROR = "You can't have an empty list item"

class ItemForm(forms.Form):
  text = forms.CharField(
    required = True,
    error_messages={'required': EMPTY_ITEM_ERROR},
  )

  def save(self, for_list):
    return Item.objects.create(
      list=for_list,
      text=self.cleaned_data['text']
    )
  
class ExistingListItemForm(ItemForm):
  
  def __init__(self, for_list, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._for_list = for_list

  def clean_text(self):
    text = self.cleaned_data['text']
    if self._for_list.item_set.filter(text=text).exists():
      raise forms.ValidationError(DUPLICATE_ITEM_ERROR)
    return text
  
  def save(self):
    return super().save(for_list=self._for_list)