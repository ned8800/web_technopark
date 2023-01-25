from django.conf import Settings
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from app import forms
from django.contrib.auth.decorators import login_required

from askme import settings
from . import models

from datetime import datetime, timezone, timedelta

from django.contrib import auth


'''
    Задачи 1
    + Логин создает юзера, а нужно профиль
    + аватарка
    + В settings добавить аватарку
    + textArea вопроса слишком большой
    + декомпозировать контроллеры
    + get_shared_context не нужен
    + проверить частные случаи
        + если, находясь на странице настроек, нажать log out - попадаешь на log in
        + неавторизованный пользователь при отправке ответа на вопрос попадет на log in
        + скролл к ответу реализована через якоря (атрибут id = id ответа)
        + после регистрации пользователь попадает на страницу вопросов
    + определить поля, обязательные для заполнения
    + включить validate
    + теги без запятой?
    + проверить выполнение всех задач с гитхаба (не все выполнены)
    - добавить лайк на ответ (сортировка ответов по рейтингу)
    
    Задачи 2
    + аватарка
    + лайк к ответу
    + сортировка ответом по лайкам, при равном количестве лайков по дате
    - пагинация при одной странице должна отсутсвовать
    - секунды, прошедшие с момента отправки ответа или вопроса, не должна содержать десятые доли
        - 4.34 ago, 6.4 ago (либо две цифры после точки, либо одна)
        - нужно пофиксить 

    Задачи 3
    + Пользователь не может удалить аватарку, добавить галочку в настройках
    + добавить отображение правильного ответа
        + не автор вопроса не может взаимодейстовать с этой кнопкой
        + при нажатии лайка или correct от неавторизованного, возникает ошибка в js
    + обработка на js лайк от незарегестрированного пользователя
    + сортировка ответов с учетом correct
    + автор вопроса отмечает один ответ корректным
    
    ? добавить дизлайк
    ? при удалении вопроса теги не удаляются, что делать с зомби-тегами
'''

COUNT_BEST_ITEMS = 10

def paginate(objects_list, request, per_page = 5):
    contact_list = objects_list
    paginator = Paginator(contact_list, per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page

def get_best_items():
    best_items = {
        'tags' : models.Tag.objects.get_popular_tags()[:COUNT_BEST_ITEMS],
        'profiles' : models.Profile.objects.get_best_profiles()[:COUNT_BEST_ITEMS]
    }
    return best_items

def get_response_404():
    return HttpResponseNotFound('<h1>Page not found</h1>')

def add_tags_to_question(tags, question):
    for tag_title in tags.split(','):
        tag = models.Tag(title = tag_title)
        try:
            tag.save()
            question.tags.add(tag)
        except IntegrityError:
            pass

def get_num_page_by_id(paginator, id):
    for i in paginator.page_range:
        entities  = paginator.page(i).object_list
        for entity in entities.all():
            if entity.id == id:
                return i 
    return None


def index(request):
    questions = models.Question.objects.get_new_questions()
    page = paginate(questions, request)
    context = { 'best_items' : get_best_items(), 'page' : page, 'is_hot' : False }
    return render(request, "index.html", context=context)


def hot(request):
    hot_questions = models.Question.objects.get_hot_questions()
    page = paginate(hot_questions, request)
    context = { 'best_items' : get_best_items(), 'page' : page, 'is_hot' : True }
    return render(request, "hot.html", context=context)


def question(request, question_id : int):
    needed_question = models.Question.objects.filter(pk=question_id).first()
    
    if not needed_question:
        return get_response_404()

    if request.method == 'GET':
        answer_form = forms.AnswerForm()
    elif request.method == 'POST':
        # неавторизированный пользователь не может отвечать на вопрос
        if not request.user.is_authenticated:
            return redirect("login")
        answer_form = forms.AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit = False)
            
            user = models.User.objects.get(username = request.user)
            answer.author = models.Profile.objects.get(user = user)

            answer.question = needed_question
            answer.save()
            answer_id = answer.id
            
            # дублирование, т.к. при GET запросе новый ответ не добавляется
            # answers = needed_question.answer_set.all().order_by('date')
            answers = needed_question.answer_set.get_sort_answers()
            page = paginate(answers, request)
            
            # получаем номер страницы, на которой разместился новый вопрос
            num_page = get_num_page_by_id(page.paginator, answer_id)
            # скроллинг по якорю: <div id="{{answer_id"}}"> </div>
            return redirect(reverse("question", args = [question_id]) + f'?page={num_page}#{answer_id}')

    answers = needed_question.answer_set.get_sort_answers()
    page = paginate(answers, request)
    context = { 'best_items' : get_best_items(), 'page' : page, 'question' : needed_question, 'form' : answer_form }
    return render(request, "question.html", context=context)

# settings.LOGIN_URL
@login_required(login_url = "login", redirect_field_name=settings.REDIRECT_FIELD_NAME)
def ask(request):
    if request.method == 'GET':
        ask_form = forms.AskForm()
    elif request.method == 'POST':
        ask_form = forms.AskForm(request.POST)
        if ask_form.is_valid():
            # получаем объект БД
            question = ask_form.save(commit = False)
            user = models.User.objects.get(username = request.user)
            question.author = models.Profile.objects.get(user = user)
            question.save()
            add_tags_to_question(ask_form.cleaned_data['tag_list'], question)
            return redirect(reverse("question", args = [question.id]))
            # почему работает?
            # return redirect("question", question_id=question.id)
    context = { 'best_items' : get_best_items(), 'form' : ask_form }
    return render(request, "ask.html", context=context)


def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            print("request.GET 1 = ", request.GET)
            url = request.GET.get('continue', '/')
            # if not url:
            #     url = '/'
            return HttpResponseRedirect(url)
        login_form = forms.LoginForm()
        print("request.GET 2 = ", request.GET)
    elif request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                print("request.POST = ", request.POST)
                print("request.POST_GET = ", request.GET)
                # return HttpResponseRedirect(reverse(viewname="register", kwargs={'continue' : '/'}))
                
                return redirect(reverse(viewname="login") + "?continue=" + request.GET.get('continue', '/'))
            else:
                login_form.add_error(None, "Username or password is incorrect")
    context = { 'best_items' : get_best_items(), 'form' : login_form }
    return render(request, "login.html", context=context)


def register(request):
    if request.method == 'GET':
        reg_form = forms.RegistrationForm()
    elif request.method == 'POST':
        reg_form = forms.RegistrationForm(data = request.POST, files = request.FILES)
        if reg_form.is_valid():
            user = reg_form.save()
            if user:
                # avatar = None ?
                auth.login(request, user)
                if reg_form.cleaned_data['avatar']:
                    models.Profile.objects.create(user = user, avatar = reg_form.cleaned_data['avatar'])
                else:
                    models.Profile.objects.create(user = user)
                    
                # models.Profile.objects.create(user = user)
                return redirect(reverse(viewname="index"))
            else:
                reg_form.add_error(None, "User saving error")
    context = { 'best_items' : get_best_items(), 'form' : reg_form }
    return render(request, "register.html", context=context)


@login_required(login_url = "login", redirect_field_name=settings.REDIRECT_FIELD_NAME)
def settings(request):
    if request.method == 'GET':
        dict_model_fields = model_to_dict(request.user)
        # инициализация формы существующими значениями
        user_form = forms.SettingsForm(initial=dict_model_fields)
    elif request.method == 'POST':
        print("request.POST >> ", request.POST)
        print("request.GET >> ", request.GET)   
        print("request.POST.Delete_avatar.... >> ", request.POST.get('Delete_avatar', 'off'))
        # print("request.POST.Delete_avatar[0].... >> ", request.POST.Delete_avatar[0])
        user_form = forms.SettingsForm(data=request.POST, files = request.FILES, instance = request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect(reverse("settings"))
    context = { 'best_items' : get_best_items(), 'form' : user_form }
    return render(request, "settings.html", context=context)


def logout(request):
    auth.logout(request)
    return redirect(request.META['HTTP_REFERER'])


def tag(request, tag_id : int):
    if not models.Tag.objects.filter(pk=tag_id).exists():
        return get_response_404()
    
    questions = models.Question.objects.get_questions_by_tag(tag_id)
    page = paginate(questions, request)
    tag = models.Tag.objects.get(id=tag_id).title
    context = { 'best_items' : get_best_items(), 'question' : questions, 'tag' :  tag, 'page' : page }
    return render(request, "tag.html", context=context)

@login_required(login_url = "login")
def like(request):
    question_id = request.POST['question_id']
    question = models.Question.objects.get(id = question_id)
    like = models.Like.objects.filter(question = question, author = request.user.profile).first()
    if not like:
        like = models.Like(question = question, author = request.user.profile)
        like.save()
    else:
        models.Like.objects.get(id = like.id).delete()
        
    return JsonResponse({"count_likes" : question.like_set.all().count() })

@login_required(login_url = "login")
def like_answer(request):
    answer_id = request.POST['answer_id']
    answer = models.Answer.objects.get(id = answer_id)
    like = models.LikeAnswer.objects.filter(answer = answer, author = request.user.profile).first()
    if not like:
        like = models.LikeAnswer(answer = answer, author = request.user.profile)
        like.save()
    else:
        models.LikeAnswer.objects.get(id = like.id).delete()
        
    return JsonResponse({"count_likes_answer" : answer.likeanswer_set.all().count() })

def get_answer_correct(question):
    for answer in question.answer_set.all():
        if answer.is_correct:
            return answer
    return False

@login_required(login_url = "login")
def correct(request):
    # авторизация проверяется на уровне js
    # запрос не приходит от неавторизированных пользователей
    print(request.POST)
    answer_id = request.POST['answer_id']
    answer = models.Answer.objects.get(id = answer_id)
    question = answer.question
    
    # ищем старый правильный ответ, убираем отметку о правильности
    # устанавливаем отметку на новом ответе
    if question.author.user == request.user:
        old_answer_correct = get_answer_correct(question)
        if old_answer_correct:
            if old_answer_correct == answer:
                answer.is_correct = False
            else:
                old_answer_correct.is_correct = False
                answer.is_correct = True
            old_answer_correct.save()
        else:
            answer.is_correct = True
        answer.save()
        return JsonResponse({
                "status" : True, 
                "correct" : answer.is_correct, 
                "old_answer_id" : f'{old_answer_correct.id}' if old_answer_correct else False
            })
    else:
        return JsonResponse({"status" : False })


# Замечания
# для перенаправления на изначальную страницу после нажатия login

# login.html    : <form action="{% url 'login' %}?continue={{request.GET.continue}}" method="post" class="form"> 
# question.html : <a href="{% url "login" %}?continue={{request.path}}" class="btn btn-outline-warning"> Войдите в систему </a>
# base.html     : href="{% url "login" %}?continue={{request.path}}