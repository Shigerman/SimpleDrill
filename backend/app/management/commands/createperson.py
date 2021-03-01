from django.contrib.auth.models import User
from django.core import management
from django.core.management.base import BaseCommand
from backend.app.models import Person


class Command(BaseCommand):
    help = "Creates a Person object from a superuser User object"

    def handle(self, *args, **options):
        superuser_name = input("Enter the superuser name: ")

        def make_superuser_a_person(superuser_name):
            superuser = User.objects.get(username=superuser_name)
            person = Person.objects.create(user=superuser)
            person.save()

        make_superuser_a_person(superuser_name)
