from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from . import models


def paginate(objects_list, request, per_page = 5):
    contact_list = objects_list
    paginator = Paginator(contact_list, per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page

# headers = request.headers
# return HttpResponse(str(headers))
@require_GET
def index(request):
    page = paginate(models.QUESTIONS, request)
    context = { 'questions' : models.QUESTIONS, 'best_items' : models.BEST_ITEMS, 'page' : page, 'is_auth' : True }
    return render(request, "index.html", context=context)

def question(request, question_id : int):
    page = paginate(models.QUESTIONS[question_id].get('answers'), request)
    context = { 'question' : models.QUESTIONS[question_id], 'best_items' : models.BEST_ITEMS, 'page' : page }
    return render(request, "question.html", context=context)

def ask(request):
    context = { 'best_items' : models.BEST_ITEMS, 'is_auth' : False }
    return render(request, "ask.html", context=context)

def login(request):
    context = { 'best_items' : models.BEST_ITEMS, 'is_auth' : False }
    return render(request, "login.html", context=context)

def register(request):
    context = { 'best_items' : models.BEST_ITEMS, 'is_auth' : False }
    return render(request, "register.html", context=context)

def settings(request):
    context = { 'best_items' : models.BEST_ITEMS, 'is_auth' : False }
    return render(request, "settings.html", context=context)

def tag(request, tag_id : int):
    context = { 'tag' : f'tag{tag_id}', 'questions' : [] }
    
    for question in models.QUESTIONS:
        for tag in question['tags']:
            if tag['tag_id'] == tag_id:
                context['questions'].append(question)
                break
                
    page = paginate(context['questions'], request)
    context['page'] = page
    return render(request, "tag.html", context=context)

# Create your views here.
