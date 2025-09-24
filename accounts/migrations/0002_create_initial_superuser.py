# from django.db import migrations

# def create_superuser(apps, schema_editor):
#     User = apps.get_model('accounts', 'User')
#     if not User.objects.filter(email='admin@example.com').exists():
#         User.objects.create_superuser(
#             full_name='Agwu Emmanuel',
#             email='emmanuelagwu89@gmail.com',
#             password='eueacj12345' 
#         )

# class Migration(migrations.Migration):

#     dependencies = [
#         ('accounts', '0001_initial'),
#     ]

#     operations = [
#         migrations.RunPython(create_superuser),
#     ]


from django.db import migrations

def create_superuser(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    if not User.objects.filter(email='admin@example.com').exists():
        user = User(
            full_name='Agwu Emmanuel',
            email='emmanuelagwu89@gmail.com',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password('eueacj123456')
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]