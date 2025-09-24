from django.db import migrations

def create_superuser(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            full_name='Agwu Emmanuel',
            email='emmanuelagwu@gmail.com',
            password='eueacj12345' 
        )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', 'PREVIOUS_MIGRATION_NAME'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]