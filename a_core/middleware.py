from django.shortcuts import redirect
from django.conf import settings
from subscriptions.models import Subscription
from datetime import datetime

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                subscription = Subscription.objects.get(profile=request.user.profile)
                if not subscription.active:
                    # Redirecione para uma página de renovação de assinatura
                    return redirect('renew_subscription')
            except Subscription.DoesNotExist:
                pass

        response = self.get_response(request)
        return response

