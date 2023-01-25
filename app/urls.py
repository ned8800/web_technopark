from app import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('hot', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('ask', views.ask, name='ask'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),
    path('tag/<int:tag_id>', views.tag, name='tag'),
]
