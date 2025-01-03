# Generated by Django 5.1.1 on 2024-11-08 01:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_userprofile_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockActive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prev_hash', models.CharField(max_length=255)),
                ('current_hash', models.CharField(max_length=255)),
                ('is_genesis', models.BooleanField()),
                ('valid_count', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='user_images/avatar.jpg', null=True, upload_to='user_images'),
        ),
        migrations.CreateModel(
            name='UserBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curlid', models.CharField(max_length=255)),
                ('hash', models.CharField(max_length=255, unique=True)),
                ('coins', models.IntegerField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wallets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BlockActiveDataJson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=255)),
                ('message', models.TextField(blank=True, null=True)),
                ('prev_hash', models.CharField(max_length=255)),
                ('type_task', models.CharField(max_length=50)),
                ('count_coins', models.IntegerField(blank=True, null=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_json', to='users.blockactive')),
                ('from_wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_transactions', to='users.userblock')),
                ('to_wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_transactions', to='users.userblock')),
            ],
        ),
    ]
