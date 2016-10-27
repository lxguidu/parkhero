#!/usr/bin/env python 
# -*- coding: utf-8 -*-

'''
Add role
Authorize role to user
'''

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string

import django
django.setup()

from django.contrib.auth.models import User

from userprofile.models import(
    UserProfile, BankCard, Vehicle, Role
)

def populate():
    add_role('administrator')
    authorize_role('administrator','sysadmin')

def add_role(name):
    role = Role.objects.get_or_create(role=name)[0]
    role.save()
    print('Added role[%s]' % name)
    return role


def authorize_role(role, owner):
    try:
        r = Role.objects.get(role=role)
        o = User.objects.get(username=owner)
        r.owner.add(o)
        r.save()
        print('Authorized [%s] as [%s]' % (owner,role))
    except (Role.DoesNotExist,User.DoesNotExist) as e:
        print('Error occurred: %s' % str(e))

    return r

# Start execution here!
if __name__ == '__main__':
    print ("Starting user_profile population script...")
    populate()

