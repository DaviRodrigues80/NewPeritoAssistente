from django.db import models
from django.contrib.auth.models import User
from a_users.models import Profile

class Plan(models.Model):
    name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    profile = models.ForeignKey('a_users.Profile', on_delete=models.CASCADE, null=True)
    stripe_subscription_id = models.CharField(max_length=255)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  
    start_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)  
    end_date = models.DateTimeField(null=True)  
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profile.user} - {self.plan.name}"