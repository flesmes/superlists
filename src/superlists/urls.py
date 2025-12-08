from django.urls import include, path
import lists.views as list_views

urlpatterns = [
    path('', list_views.home_page, name='home'),
    path('lists/', include('lists.urls')),
]
