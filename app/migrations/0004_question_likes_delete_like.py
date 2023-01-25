
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_answer_date_alter_question_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='likes',
            field=models.ManyToManyField(related_name='related_likes', to='app.profile'),
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
