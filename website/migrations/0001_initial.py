# Generated by Django 3.1.7 on 2021-03-29 04:58

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Human',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('session', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('type', models.IntegerField(choices=[(1, 'Normal')], default=1)),
                ('username', models.CharField(max_length=64)),
                ('username_unique', models.CharField(max_length=64, unique=True)),
                ('password', models.CharField(max_length=64)),
                ('bio', models.TextField(blank=True, default='', null=True)),
                ('phone_number', models.CharField(max_length=16, unique=True)),
                ('email', models.EmailField(max_length=64, unique=True)),
                ('real_name', models.CharField(help_text='Full real name', max_length=64)),
                ('profile_image', models.CharField(blank=True, default=None, max_length=96, null=True)),
                ('blocked', models.BooleanField(default=False)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, default='', null=True)),
                ('lat', models.FloatField(default=0, help_text='Latitude')),
                ('lng', models.FloatField(default=0, help_text='Longitude')),
                ('elv', models.FloatField(default=0, help_text='Elevation')),
                ('status', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3)], default=1)),
                ('nft_count', models.IntegerField(default=0)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('human', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.human')),
            ],
        ),
        migrations.CreateModel(
            name='Nft',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, default='', null=True)),
                ('url', models.URLField(blank=True, default='', null=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('land', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.land')),
            ],
        ),
    ]
