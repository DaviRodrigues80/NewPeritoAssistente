from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.db.models import Q
from a_users.models import Profile
from cryptography.fernet import Fernet
from django.conf import settings
from .forms import InboxNewMessageForm
from .models import *

f = Fernet(settings.ENCRYPT_KEY)


@login_required
def inbox_view(request, conversation_id=None):
    my_conversations = Conversation.objects.filter(participants=request.user)
    print('minhas conversas:', my_conversations)
    if conversation_id:
        conversation = get_object_or_404(my_conversations, id=conversation_id)
        print('conversa:', conversation)
        latest_message = conversation.messages.first()
        if conversation.is_seen == False and latest_message.sender != request.user:
            conversation.is_seen = True
            print('conversa:', conversation)
            conversation.save()
            
            # Decodificar as mensagens antes de passar para o template
            for message in conversation.messages.all():
                if message.body_encrypted:
                    try:
                        message.body = f.decrypt(message.body_encrypted.encode()).decode()
                    except Exception as e:
                        # Lida com possíveis erros de descriptografia
                        print(f"Erro ao descriptografar mensagem: {e}")
    else:
        conversation = None
    context = {
        'conversation': conversation,
        'my_conversations': my_conversations
    }
    return render(request, 'a_inbox/inbox.html', context)


def search_users(request):
    if request.htmx:
        letters = request.GET.get('search_user', '').strip()
        print(f"Letters received for search: {letters}")
        
        if letters:
            profiles = Profile.objects.filter(realname__icontains=letters)
            print(f"Profiles matching the letters: {profiles}")

            users_id = profiles.values_list('user', flat=True)
            print(f"User IDs from profiles: {users_id}")

            users = User.objects.filter(
                Q(username__icontains=letters) | Q(id__in=users_id)
            ).exclude(username=request.user.username)
            print(f"Users found: {users}")

            return render(request, 'a_inbox/list_searchuser.html', {'users': users})
        else:
            print("No letters provided or letters are empty.")
            return HttpResponse('')
    else:
        print("Request is not an HTMX request.")
        raise Http404()

    

@login_required     
def new_message(request, recipient_id):
    recipient = get_object_or_404( User, id=recipient_id)
    new_message_form = InboxNewMessageForm()
    
    if request.method == 'POST':
        form = InboxNewMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)

            # encrypt message
            message_original = form.cleaned_data['body']
            message_bytes = message_original.encode('utf-8')
            message_encrypted = f.encrypt(message_bytes)
            message_decoded = message_encrypted.decode('utf-8')
            message.body = message_decoded
            
            print('message_original:', message_original)
            print('message_bytes:', message_bytes)
            print('message_encrypted:', message_encrypted)
            print('message_decoded:', message_decoded)
            
            
            message_decrypted = f.decrypt(message_decoded)
            message_decoded = message_decrypted.decode('utf-8')
            
            print('message_decrypted:', message_decrypted)
            print('message_decoded:', message_decoded)
            
            
            
            message.sender = request.user
            
            my_conversations = request.user.conversations.all()
            for c in my_conversations:
                if recipient in c.participants.all():
                    message.conversation = c
                    message.save()
                    c.lastmessage_created = timezone.now()
                    c.is_seen = False
                    c.save()
                    return redirect('inbox', c.id)
            new_conversation = Conversation.objects.create()
            new_conversation.participants.add(request.user, recipient)
            new_conversation.save()
            message.conversation = new_conversation
            message.save() 
            return redirect('inbox', new_conversation.id)
    
    context = {
        'recipient': recipient,
        'new_message_form': new_message_form
    }
    return render(request, 'a_inbox/form_newmessage.html', context)



@login_required
def new_reply(request, conversation_id):
    new_message_form = InboxNewMessageForm()
    my_conversations = request.user.conversations.all()
    conversation = get_object_or_404(my_conversations, id=conversation_id)
    
    if request.method == 'POST':
        form = InboxNewMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)

            # encrypt message
            message_original = form.cleaned_data['body']
            message_bytes = message_original.encode('utf-8')
            message_encrypted = f.encrypt(message_bytes)
            message_decoded = message_encrypted.decode('utf-8')
            message.body = message_decoded
            
            message.sender = request.user
            message.conversation = conversation
            message.save()
            conversation.lastmessage_created = timezone.now()
            conversation.is_seen = False
            conversation.save()
            return redirect('inbox', conversation.id)
    
    context = {
        'new_message_form': new_message_form,
        'conversation' : conversation
    }
    return render(request, 'a_inbox/form_newreply.html', context)



def notify_newmessage(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    latest_message = conversation.messages.first()
    if conversation.is_seen == False and latest_message.sender != request.user:
        return render(request, 'a_inbox/notify_icon.html', {'new_messages': True})
    else:
        return render(request, 'a_inbox/notify_icon.html', {'new_messages': False})

def notify_inbox(request):
    my_conversations = Conversation.objects.filter(participants=request.user, is_seen=False)
    new_messages = any(c.messages.first().sender != request.user for c in my_conversations)
    return render(request, 'a_inbox/notify_icon.html', {'new_messages': new_messages})