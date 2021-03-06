# Generated by Django 3.1.7 on 2021-04-05 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_ethaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='human',
            name='bio',
            field=models.TextField(blank=True, default='Bio', null=True),
        ),
        migrations.AlterField(
            model_name='human',
            name='profile_image',
            field=models.CharField(blank=True, default='/static/images/user-default.png', max_length=256, null=True),
        ),
    ]
