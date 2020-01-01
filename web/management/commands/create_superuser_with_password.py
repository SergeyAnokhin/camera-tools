import os
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
# from https://stackoverflow.com/questions/6244382/how-to-automate-createsuperuser-on-django
# from https://github.com/adamcharnock/swiftwind-heroku/blob/master/swiftwind_heroku/management/commands/create_superuser_with_password.py

class Command(createsuperuser.Command):
    help = 'Crate a superuser, and get password from environment variable DJANGO_ADMIN_PASSWORD'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--preserve', dest='preserve', default=False, action='store_true',
            help='Exit normally if the user already exists.',
        )

    def handle(self, *args, **options):
        print("Run modified createsuperuser")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")
        username = options.get('username')
        database = options.get('database')

        if password and not username:
            raise CommandError("--username is required if specifying variable DJANGO_ADMIN_PASSWORD")

        if username and options.get('preserve'):
            exists = self.UserModel._default_manager.db_manager(database).filter(username=username).exists()
            if exists:
                self.stdout.write("User exists, exiting normally due to --preserve")
                return

        super(Command, self).handle(*args, **options)

        if password:
            user = self.UserModel._default_manager.db_manager(database).get(username=username)
            user.set_password(password)
            user.save()