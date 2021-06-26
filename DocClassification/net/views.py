from .models import Queries
from .forms import QueryForm
from .recognizer import cnn, name_map, inv_name_map, vocab, preprocess
from .text_extractor import get_text_pdf, get_text_docx, get_text_pptx, get_text_xlsx, get_text_msg

import os
import torch

from django.contrib import messages
from django.shortcuts import render
from django.core.files import File
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse, reverse_lazy

# Create your views here.
def main(request):
	context = {
		'name': 'Hello world'
	}
	template = 'main.html'
	return render(request, template, context)

def upload_query(request):
	if request.method == 'POST':
		form = QueryForm(request.POST, request.FILES)
		if form.is_valid():
			item = Queries()
			item.attach = form.cleaned_data['attach']
			print(item.attach)
			item.save()
			return redirect(reverse('check_document', args=(item.pk, )))
	else:
		form = QueryForm()
	return render(request, 'upload_query.html', {'form': form})

def check_document(request, pk):
	q = Queries.objects.get(pk=pk)

	filename, file_extension = os.path.splitext(q.attach.path)
	if file_extension == '.pdf':
		try:
			text = get_text_pdf(q.attach.path)
		except:
			messages.error(request, 'Problem with file')
			return redirect(reverse('upload_query'))
	elif file_extension == '.docx':
		try:
			text = get_text_docx(q.attach.path)
		except:
			messages.error(request, 'Problem with file')
			return redirect(reverse('upload_query'))
	elif file_extension == '.pptx':
		try:
			text = get_text_pptx(q.attach.path)
		except:
			messages.error(request, 'Problem with file')
			return redirect(reverse('upload_query'))
	elif file_extension == '.xlsx':
		try:
			text = get_text_xlsx(q.attach.path)
		except:
			messages.error(request, 'Problem with file')
			return redirect(reverse('upload_query'))
	elif file_extension == '.msg' or file_extension == '.eml':
		try:
			text = get_text_msg(q.attach.path)
		except:
			messages.error(request, 'Problem with file')
			return redirect(reverse('upload_query'))
	elif file_extension == '.txt':
		try:
			with open(q.attach.path, 'r') as f:
				text = f.read()
		except:
			messages.error(request, 'Problem with file')
			return redirect(reverse('upload_query'))
	else:
		messages.error(request, 'Bad format of file')
		form = QueryForm()
		return redirect(reverse('upload_query'))

	inp = preprocess(text, vocab)
	try:
		out = cnn(torch.LongTensor(inp).unsqueeze(0).cuda()).squeeze(0).tolist()
	except:
		messages.error(request, 'Problem with file')
		return redirect(reverse('upload_query'))

	result = []
	for k,o in enumerate(out):
		if o>0.2:
			result.append([inv_name_map[k], o])
	context = {
		'result': sorted(result, key=lambda x: x[1], reverse=True),
	}
	return render(request, 'result_page.html', context)