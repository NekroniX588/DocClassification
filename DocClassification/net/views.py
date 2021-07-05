from .models import Queries
from .forms import QueryForm, FileFieldForm
from .recognizer import cnn, name_map, inv_name_map, vocab, preprocess
from .text_extractor import get_text_pdf, get_text_docx, get_text_pptx, get_text_xlsx, get_text_msg

import os
import json
import uuid
import torch
from treelib import Node, Tree
from collections import Counter

from django.contrib import messages
from django.shortcuts import render
from django.core.files import File
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse, reverse_lazy

def make_tree(tree, results, root, layer):
	idx = uuid.uuid1().hex
	if len(results) == 1:
		tree.create_node(str(results[0][0]),idx,parent=root, data=[str(results[0][1])])
		return
	
	most_common = Counter([r[0] for r in results]).most_common(1)[0][0]
	files = []
	need = []
	noneed = []
	for r in results:
		if r[0] == most_common:
			files.append(r[1])
	for r in results:
		if r[1] in files and r[0] != most_common:
			need.append(r)
		elif r[1] not in files and r[0] != most_common:
			noneed.append(r)
	if len(need) == 0:
		tree.create_node(most_common, idx, parent=root, data=files)
	else:
		tree.create_node(most_common, idx, parent=root)
	if len(need)>0:
		make_tree(tree, need, idx, layer+1)
	if len(noneed)>0:
		make_tree(tree, noneed, root, layer+1)

def make_show(show, name, node, layer):
	if 'children' in node:
		show.append(['__'*layer+name, ''])
		for j in range(len(node['children'])):
			name = list(node['children'][j].keys())[0]
			make_show(show, name, node['children'][j][name], layer+1)
	else:
		show.append(['__'*layer+name, ','.join(node['data'])])

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


def upload_many(request):
	if request.method == 'POST':
		form = FileFieldForm(request.POST, request.FILES)
		files = request.FILES.getlist('file_field')
		results = []

		if form.is_valid():
			for file in files:
				with open(os.path.join('./tmp',str(file)), 'wb+') as f:
					for chunk in file.chunks():
						f.write(chunk)
			for file in os.listdir('./tmp'):
				filename, file_extension = os.path.splitext(file)
				if file_extension == '.pdf':
					try:
						text = get_text_pdf(os.path.join('./tmp',str(file)))
					except:
						messages.error(request, 'Problem with file:'+str(file))
						continue
				elif file_extension == '.docx':
					try:
						text = get_text_docx(os.path.join('./tmp',str(file)))
					except:
						messages.error(request, 'Problem with file:'+str(file))
						continue
				elif file_extension == '.pptx':
					try:
						text = get_text_pptx(os.path.join('./tmp',str(file)))
					except:
						messages.error(request, 'Problem with file:'+str(file))
						continue
				elif file_extension == '.xlsx':
					try:
						text = get_text_xlsx(os.path.join('./tmp',str(file)))
					except:
						messages.error(request, 'Problem with file:'+str(file))
						continue
				elif file_extension == '.msg' or file_extension == '.eml':
					try:
						text = get_text_msg(os.path.join('./tmp',str(file)))
					except:
						messages.error(request, 'Problem with file:'+str(file))
						continue
				elif file_extension == '.txt':
					try:
						with open(os.path.join('./tmp',str(file)), 'r') as f:
							text = f.read()
					except:
						messages.error(request, 'Problem with file:'+str(file))
						continue
				inp = preprocess(text, vocab)
				try:
					out = cnn(torch.LongTensor(inp).unsqueeze(0).cuda()).squeeze(0).tolist()
				except:
					messages.error(request, 'Problem with file:'+str(file))
					continue
				for k,o in enumerate(out):
					if o>0.5:
						results.append([inv_name_map[k], file])
			tree = Tree()
			tree.create_node('start','root')
			make_tree(tree, results, 'root', 1)

			d = json.loads(tree.to_json(with_data=True))
			show = []
			make_show(show,'start',d['start'],-1)

			for file in os.listdir('./tmp'):
				os.remove(os.path.join('./tmp',str(file)))
			context = {
				'show':show[1:],
			}
			return render(request, 'result_many.html', context)
	else:
		form = FileFieldForm()
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