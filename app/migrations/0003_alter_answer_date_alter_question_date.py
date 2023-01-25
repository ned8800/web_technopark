
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_profile_avatar_alter_question_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='question',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
