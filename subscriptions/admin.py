from django.contrib import admin
from .models import Subscription,Plan


admin.site.register(Plan)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'plan', 'amount', 'start_date', 'end_date', 'active']
    list_filter = ['active', 'plan']
    search_fields = ['profile__user__username', 'stripe_subscription_id']