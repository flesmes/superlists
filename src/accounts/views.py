from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse

def send_login_email(request):
  SUBJECT = 'Your login link for Superlists'
  FROM_EMAIL = 'noreply@flesmes.com'
  to_email = request.POST['email']
  body = 'Use this link to log in'
  send_mail(SUBJECT, body, FROM_EMAIL, [to_email])
  messages.success(
    request,
    'Check your email, we\'ve sent you a link you can use to log in.'
  )
  return redirect(reverse('home'))
