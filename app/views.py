from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from . import models

from datetime import datetime, timezone, timedelta

COUNT_BEST_ITEMS = 10

def paginate(objects_list, request, per_page = 5):
    contact_list = objects_list
    paginator = Paginator(contact_list, per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    print(page)
    print(type(page))
    print(page.object_list)
    return page

def get_best_items():
    best_items = {
        'tags' : models.Tag.objects.get_popular_tags()[:COUNT_BEST_ITEMS],
        'profiles' : models.Profile.objects.get_best_profiles()[:COUNT_BEST_ITEMS]
    }
    return best_items

def get_shared_context():
    return {
        'best_items'    : get_best_items(),
        'is_auth'       : True 
    }
    

def index(request):
    questions = models.Question.objects.get_new_questions()
    page = paginate(questions, request)
    context = get_shared_context()
    context['page'] = page
    context['is_hot'] = False
    return render(request, "index.html", context=context)

def hot(request):
    # hot_questions = get_list_hot_questions_from_db()
    hot_questions = models.Question.objects.get_hot_questions()
    page = paginate(hot_questions, request)
    context = get_shared_context()
    context['page'] = page
    context['is_hot'] = True
    return render(request, "hot.html", context=context)

def question(request, question_id : int):
    needed_question = models.Question.objects.filter(pk=question_id)
    if not needed_question.exists():
        return HttpResponseNotFound('<h1>Page not found</h1>')
    needed_question = needed_question[0]
    answers = needed_question.answer_set.all()
    page = paginate(answers, request)
    context = get_shared_context()
    context['question'] = needed_question
    context['page'] = page
    return render(request, "question.html", context=context)

def ask(request):
    context = get_shared_context()
    return render(request, "ask.html", context=context)

def login(request):
    context = get_shared_context()
    return render(request, "login.html", context=context)

def register(request):
    context = get_shared_context()
    return render(request, "register.html", context=context)

def settings(request):
    context = get_shared_context()
    # Test form "log in"
    context['is_auth'] = False
    return render(request, "settings.html", context=context)

def tag(request, tag_id : int):
    if not models.Tag.objects.filter(pk=tag_id).exists():
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
    questions = models.Question.objects.get_questions_by_tag(tag_id)
    page = paginate(questions, request)
    context = get_shared_context()
    context['question'] = questions
    context['tag'] = context['tag'] = models.Tag.objects.get(id=tag_id).title
    context['page'] = page
    return render(request, "tag.html", context=context)

