# subscriptions/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.subscription, name='create_subscription'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('sucesso/', views.pag_sucesso, name='pag_sucesso'),
    path('cancelado/', views.pag_cancelado, name='pag_cancelado'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('subscription-list/', views.subscription_list, name='subscription-list'),
]