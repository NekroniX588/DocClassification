from .models import Queries

from django import forms
from django.forms import Textarea
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class QueryForm(forms.ModelForm):
 
	class Meta:
		model = Queries
		fields = ['attach']
        
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'
			self.fields[field].widget.attrs['accept'] = ".pdf, .docx, .pptx, .xlsx, .eml, .msg, .txt"

class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))