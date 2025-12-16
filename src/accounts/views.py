from django.contrib import auth, messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import Token

def send_login_email(request):
  SUBJECT = 'Your login link for Superlists'
  FROM_EMAIL = 'noreply@flesmes.com'
  to_email = request.POST['email']
  token = Token.objects.create(email=to_email)
  relative_url = reverse('login', query={'token': str(token.uid)})
  url = request.build_absolute_uri(relative_url)
  body = f'Use this link to log in:\n\n{url}'
  send_mail(SUBJECT, body, FROM_EMAIL, [to_email])
  messages.success(
    request,
    'Check your email, we\'ve sent you a link you can use to log in.'
  )
  return redirect(reverse('home'))

def login(request):
  user = auth.authenticate(uid=request.GET['token'])
  if user:
    auth.login(request, user)
  else:
    messages.error(request,'Invalid login link, please request a new one')
  return redirect(reverse('home'))
