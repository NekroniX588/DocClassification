from django.shortcuts import render
from .models import Queries
from .forms import QueryForm
from .recognizer import cnn, name_map, inv_name_map, vocab, preprocess

import torch

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
			item.save()
#             handle_uploaded_file(request.FILES['file'])
			return redirect(reverse('check_document', args=(item.pk, )))
	else:
		form = QueryForm()
	return render(request, 'upload_query.html', {'form': form})

def check_document(request, pk):
	q = Queries.objects.get(pk=pk)


	with open(q.attach.path, 'r') as f:
		text = f.read()
	print(text)
	inp = preprocess(text, vocab)

	out = cnn(torch.LongTensor(inp).unsqueeze(0).cuda()).squeeze(0).tolist()

	result = []
	for k,o in enumerate(out):
		if o>0.5:
			result.append([inv_name_map[k], o])
	print(result)
	context = {
		'result': result,
	}
	return render(request, 'result_page.html', context)