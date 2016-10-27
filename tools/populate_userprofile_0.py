import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string

import django
from django.contrib.auth.models import User

django.setup()

from userprofile.models import UserProfile, BankCard, Vehicle


def populate():
    user_tom = add_user('15307935896')

    add_bank_card(owner=user_tom, number='100001')
    add_vehicle(owner=user_tom, plate_number='100002')

    user_jack = add_user('Jack')

    add_bank_card(owner=user_jack, number='200001')
    add_vehicle(owner=user_jack, plate_number='200002')

    user_mike = add_user('Mike')

    add_bank_card(owner=user_mike, number='300001')
    add_vehicle(owner=user_mike, plate_number='300002')


    # Print out what we have added to the user.
    for u in User.objects.all():
        for c in BankCard.objects.filter(owner=u):
            print ('- {0} - {1}'.format(str(u), str(c)))

        for v in Vehicle.objects.filter(owner=u):
            print ('- {0} - {1}'.format(str(u), str(v)))


def add_user(name):
    #try:
    #    u = UserProfile.objects.get(user.username='Tom')
    #except UserProfile.DoesNotExist:
    #    u = UserProfile(user.name=name)
    #    u.save()
    #    return u
    #    pass

    u = User.objects.get_or_create(username=name)[0]
    up = UserProfile.objects.get_or_create(user=u)[0]
    u.is_staff=True
    u.set_password('asd')
    u.save()
    up.account_balance = 1000
    up.save()
    return u

def add_bank_card(owner, number):
    c = BankCard.objects.get_or_create(owner=owner)[0]
    c.number = number
    c.save()
    return c

def add_vehicle(owner, plate_number):
    v = Vehicle.objects.get_or_create(plate_number=plate_number)[0]
    v.owner.add(owner)
    v.save()
    return v

# Start execution here!
if __name__ == '__main__':
    print ("Starting user_profile population script...")
    populate()

