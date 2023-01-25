from django.db import models
import random

QUESTIONS = [
    { 
     "id"       : question_id,
     'title'    : f'Question #{question_id}',
     'text'     : f'Text of Question #{question_id}',
     'tags' : [
        {
            'tag_id' : id,
            'text' : f'tag{id}'
        } for id in list(set([random.randint(0, 10) for _ in range(random.randint(1, 10))]))
        ],
     'answers' : [
        {
            'id'            : answer_id,
            'text'          : f'Text of Answer #{answer_id}',
            'is_correct'    : answer_id == 1,
        } for answer_id in range(random.randint(1, 10))
     ],
    } for question_id in range(20)
]

BEST_ITEMS = {
    'popular_tags' : [
        {
            'tag_id' : id,
            'text' : f'tag{id}'
        } for id in [random.randint(0, 10) for _ in range(random.randint(1, 10))]
        ],
    'best_users' : [
        f'Name{i} Surname{i * i}' for i in range(5)
    ]
}



# Create your models here.
