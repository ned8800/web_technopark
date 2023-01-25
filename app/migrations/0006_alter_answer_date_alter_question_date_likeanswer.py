
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_question_likes_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='LikeAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.answer')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.profile')),
            ],
            options={
                'unique_together': {('answer', 'author')},
            },
        ),
    ]
