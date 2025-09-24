# from django.db import migrations

# def create_superuser(apps, schema_editor):
#     from django.contrib.auth import get_user_model
#     User = get_user_model()
#     if not User.objects.filter(username='admin').exists():
#         User.objects.create_superuser(
#             username='admin',
#             email='admin@example.com',
#             password='yourpassword123'
#         )

# class Migration(migrations.Migration):
#     dependencies = [
#         # add your dependencies here
#     ]

#     operations = [
#         migrations.RunPython(create_superuser),
#     ]

from django.db import migrations

def create_superuser(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            full_name='Agwu Emmanuel',
            email='emmanuelagwu89@gmail.com',
            password='eueacj12345'
        )

class Migration(migrations.Migration):

    dependencies = [
        # Make sure this is set to the latest migration in your accounts app
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]