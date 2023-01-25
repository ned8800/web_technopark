
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_answer_date_alter_question_date_likeanswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='mery.jpg', null=True, upload_to='avatars/%Y/%m/%d'),
        ),
    ]
