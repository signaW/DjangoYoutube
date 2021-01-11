# Generated by Django 3.0.5 on 2020-04-26 05:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('video_key', models.CharField(max_length=12)),
                ('upload_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('category', models.TextField(blank=True, choices=[('music', 'Music'), ('movie', 'Movie'), ('drama', 'Drama'), ('comedy', 'Comedy'), ('info', 'Information'), ('daily', 'Daily'), ('beauty', 'Beauty'), ('art', 'Art'), ('book', 'Book'), ('sport', 'Sport'), ('food', 'Food')])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('likes_user', models.ManyToManyField(blank=True, related_name='likes_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-upload_date'],
            },
        ),
    ]
