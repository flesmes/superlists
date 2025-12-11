from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from lists.models import Item, List

def home_page(request):
  return render(request, 'home.html')

def view_list(request, list_id):
  current_list = List.objects.get(id=list_id)
  error = None

  if request.method == 'POST':
    try:
      item = Item(text=request.POST['item_text'], list=current_list)
      item.full_clean()
      item.save()
      return redirect(current_list)
    except ValidationError:
      error = 'You can\'t have an empty list item'

  return render(
    request, 
    'list.html', 
    {'list': current_list, 'error': error}
  )

def new_list(request):
  new_list = List.objects.create()
  item = Item(text=request.POST['item_text'], list=new_list)

  try:
    item.full_clean()
    item.save()
  except ValidationError:
    new_list.delete()
    error = 'You can\'t have an empty list item'
    return render(request, 'home.html', {'error': error})
  
  return redirect(new_list)


