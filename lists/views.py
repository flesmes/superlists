from django.shortcuts import redirect, render
from lists.models import Item, List

def home_page(request):
  return render(request, 'home.html')

def new_list(request):
  newlist = List.objects.create()
  Item.objects.create(text=request.POST['item_text'], list=newlist)
  return redirect('/lists/single/')

def view_list(request):
  items = Item.objects.all()
  return render(request, 'list.html', {'items': items})
  return render(request, 'home.html')
