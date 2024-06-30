from django.forms import ModelForm
from django import forms
from .models import *


class PostCreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ['artist','body', 'tags',]
        labels = {
            'artist': 'Nome',
            'body' : 'Bio',
            'tags' : 'Categoria'
        }
        widgets = {
            'body' : forms.Textarea(attrs={'rows': 3, 'placeholder': 'Fale de você...', 'class': 'font1 text-1xl'}),
            'tags' : forms.CheckboxSelectMultiple(),
        }
        
        
class PostEditForm(ModelForm):
    class Meta:
        model = Post
        fields = ['body', 'tags']
        labels = {
            'body' : '',
            'tags' : 'Category'
        }
        widgets = {
            'body' : forms.Textarea(attrs={'rows': 3, 'class': 'font1 text-4xl'}),
            'tags' : forms.CheckboxSelectMultiple(),
        }
        
        
class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body' : forms.TextInput(attrs={'placeholder': 'Conversar...'})
        }
        labels = {
            'body': ''
        }
        
        
class ReplyCreateForm(ModelForm):
    class Meta:
        model = Reply
        fields = ['body']
        widgets = {
            'body' : forms.TextInput(attrs={'placeholder': 'Conversar ...', 'class': "!text-sm"})
        }
        labels = {
            'body': ''
        }