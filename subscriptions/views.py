# subscription/views.py
from django.db.models import Sum
from django.http import Http404, JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.urls import reverse
import stripe
import json
import logging
from datetime import datetime, timedelta
from a_users.models import Profile
from a_users.views import profile_view
from django.views.decorators.http import require_POST
from .models import Plan, Subscription
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

# stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)




def get_user_id(request):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user=request.user)
        profile_id = profile.id
        print(f'O id do perfil do usuário é: {profile_id}')
        return profile_id  # Retorna apenas o ID do perfil
    else:
        raise Http404("Usuário não autenticado")


def plan_list(request):
    plans = Plan.objects.all()
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    context = {
        'plans': plans,
        'stripe_publishable_key': stripe_publishable_key,
    }
    return render(request, 'plan_list.html', context)


# View para renderizar a página de assinatura
@login_required
def subscription(request):
    stripe_key = settings.STRIPE_PUBLISHABLE_KEY
    user_id_profile = get_user_id(request)
    print(f"O user_id_profile é: {user_id_profile}")
    return render(request, 'create_subscription.html', {'STRIPE_PUBLISHABLE_KEY': stripe_key, 'user_id_profile': user_id_profile})

# Determine o URL base com base na configuração DEBUG
BASE_URL = "http://localhost:8000" if settings.DEBUG else "https://novoperitoassistente.up.railway.app"

# View para criar uma sessão de checkout
@csrf_exempt
def create_checkout_session(request):
    print("create_checkout_session foi chamada")
    
    if request.method == 'POST':
        print("POST request received")
        data = json.loads(request.body)
        print(f"Data received: {data}")
        price_id = data.get('priceId')
        print(f"Price ID: {price_id}")
        client_reference_id = data.get('clientReferenceId')
        print(f"Cliente id referencia: {client_reference_id}")
        
        try:
            success_url = request.build_absolute_uri(reverse('pag_sucesso')) + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri(reverse('pag_cancelado'))
            print(f"Success URL: {success_url}")
            print(f"Cancel URL: {cancel_url}")
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=client_reference_id,
            )
            print(f"linha 65 - Sessão Stripe criada: {session.id}")
            print(f"linha 66 - Sessão Stripe criada: {session}")
            return JsonResponse({'id': session.id})
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método de solicitação inválido'}, status=400)



# View para lidar com webhooks do Stripe
@method_decorator(csrf_exempt, name="dispatch")
def stripe_webhook(request):
    print("stripe_webhook called")
    logger.info("Webhook received")
    
    payload = request.body
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    logger.info(f"Payload: {payload}")
    logger.info(f"Signature Header: {sig_header}")
    print(f"Payload: {payload}")
    print(f"Signature Header: {sig_header}")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        logger.info(f"Event: {event}")
        print(f"Event: {event}")
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        print(f"Invalid payload: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        print(f"Invalid signature: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    
    print("linha 155 - vai entrar na chamada da handle_checkout_session")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Checkout session completed: {session}")
        print(f"Checkout session completed: {session}")
        print("linha 160 - vai entrar na chamada da handle_checkout_session")
        handle_checkout_session(session)
    else:
        logger.debug(f"Evento não tratado: {event['type']}")
        print(f"Unhandled event type: {event['type']}")

    return JsonResponse({'status': 'success'}, status=200)


# Função para processar uma sessão de checkout completada
def handle_checkout_session(session):
    client_reference_id = session.get('client_reference_id')
    stripe_subscription_id = session.get('subscription')
    profile = get_object_or_404(Profile, id=client_reference_id)
    plan = get_object_or_404(Plan, price_id=session['display_items'][0]['plan']['id'])

    subscription, created = Subscription.objects.get_or_create(
        profile=profile,
        stripe_subscription_id=stripe_subscription_id,
        defaults={
            'plan': plan,
            'amount': session['display_items'][0]['amount_total'] / 100,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timezone.timedelta(days=30),  # Exemplo para 30 dias de assinatura
            'active': True,
        }
    )

    if not created:
        subscription.plan = plan
        subscription.amount = session['display_items'][0]['amount_total'] / 100
        subscription.start_date = timezone.now()
        subscription.end_date = timezone.now() + timezone.timedelta(days=30)
        subscription.active = True
        subscription.save()

@login_required
@staff_member_required  # Apenas usuários superusuários podem acessar esta view
def subscription_list(request):
    if request.user.is_superuser:
        subscriptions = Subscription.objects.all()
    else:
        subscriptions = Subscription.objects.filter(profile=request.user.profile)
        
    # Calcular o total dos valores somados de todos os planos
    total_amount = subscriptions.aggregate(total=Sum('amount'))['total'] or 0  # Retorna 0 se não houver assinaturas
    
    # Crie um dicionário para armazenar cada assinatura com seu respectivo nome de usuário
    subscriptions_with_username = []
    for subscription in subscriptions:
        # Obtém o nome de usuário do perfil associado à assinatura
        username = subscription.profile.user.username
        subscriptions_with_username.append({
            'subscription': subscription,
            'username': username,
        })
    
    return render(request, 'subscription_list.html', {'subscriptions': subscriptions_with_username, 'total_amount': total_amount})


def pag_sucesso(request):
    # Add a success message to the user's session
    messages.success(request, 'Pagamento realizado com sucesso!')

    # Redirect the user to the homepage
    return redirect('home')

# View para página de cancelamento
def pag_cancelado(request):
    
    messages.success(request, 'Pagamento cancelado!')
    
    return render(request, 'create_subscription')
