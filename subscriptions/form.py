# No seu arquivo forms.py dentro do seu aplicativo
from django import forms

class PaymentForm(forms.Form):
    session_id = forms.CharField()
    amount_total = forms.DecimalField(max_digits=10, decimal_places=2)
    client_reference_id = forms.IntegerField()
