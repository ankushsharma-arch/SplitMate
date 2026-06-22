from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from groups.models import Group
from expenses.models import Expense, ExpenseSplit
from payments.models import Payment


class Command(BaseCommand):
    help = 'Seed sample data for SplitMate interview session'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Users
        users = []
        data  = [
            ('arjun',  'arjun@example.com',  'Arjun',  'Sharma'),
            ('priya',  'priya@example.com',  'Priya',  'Mehta'),
            ('rahul',  'rahul@example.com',  'Rahul',  'Verma'),
            ('sneha',  'sneha@example.com',  'Sneha',  'Patel'),
            ('vikram', 'vikram@example.com', 'Vikram', 'Singh'),
        ]
        for username, email, first, last in data:
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first, 'last_name': last}
            )
            u.set_password('password123')
            u.save()
            users.append(u)

        arjun, priya, rahul, sneha, vikram = users

        # Group 1 — Goa Trip
        g1, _ = Group.objects.get_or_create(
            name='Goa Trip',
            defaults={
                'description': 'March trip to Goa',
                'currency': 'INR',
                'created_by': arjun,
            }
        )
        g1.members.set([arjun, priya, rahul, sneha])

        # Group 2 — Office Lunches
        g2, _ = Group.objects.get_or_create(
            name='Office Lunches',
            defaults={
                'description': 'Weekly team lunch pool',
                'currency': 'INR',
                'created_by': priya,
            }
        )
        g2.members.set([arjun, priya, rahul, vikram])

        # Expenses — Goa Trip
        if not Expense.objects.filter(group=g1).exists():
            hotel = Expense.objects.create(
                group=g1, description='Hotel stay', amount=8000,
                currency='INR', paid_by=arjun
            )
            for u in [arjun, priya, rahul, sneha]:
                ExpenseSplit.objects.create(expense=hotel, user=u, amount=2000)

            cab = Expense.objects.create(
                group=g1, description='Airport cab', amount=600,
                currency='INR', paid_by=priya
            )
            for u in [arjun, priya, rahul, sneha]:
                ExpenseSplit.objects.create(expense=cab, user=u, amount=150)

            dinner = Expense.objects.create(
                group=g1, description='Beach dinner', amount=3200,
                currency='INR', paid_by=rahul
            )
            for u in [arjun, priya, rahul, sneha]:
                ExpenseSplit.objects.create(expense=dinner, user=u, amount=800)

        # Expenses — Office Lunches
        if not Expense.objects.filter(group=g2).exists():
            lunch1 = Expense.objects.create(
                group=g2, description='Biryani Monday', amount=1200,
                currency='INR', paid_by=vikram
            )
            for u in [arjun, priya, rahul, vikram]:
                ExpenseSplit.objects.create(expense=lunch1, user=u, amount=300)

        self.stdout.write(self.style.SUCCESS('Done. Users: arjun, priya, rahul, sneha, vikram (password: password123)'))
