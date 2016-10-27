import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string

import django
django.setup()

from parking.models import ParkingLot, ParkingSpace


def populate():
    tech_lot = add_lot('tech')

    add_space(number='100001', lot=tech_lot)
    add_space(number='100002', lot=tech_lot)
    add_space(number='100003', lot=tech_lot)
    add_space(number='100004', lot=tech_lot)

    temple_lot = add_lot('temple')

    add_space(number='100001', lot=temple_lot)
    add_space(number='100002', lot=temple_lot)
    add_space(number='100003', lot=temple_lot)
    add_space(number='100004', lot=temple_lot)

    bench_lot = add_lot('bench')

    add_space(number='100001', lot=bench_lot)
    add_space(number='100002', lot=bench_lot)
    add_space(number='100003', lot=bench_lot)
    add_space(number='100004', lot=bench_lot)


    # Print out what we have added to the user.
    for l in ParkingLot.objects.all():
        for s in ParkingSpace.objects.filter(parking_lot=l):
            print ('- {0} - {1}'.format(str(l), str(s)))

def add_space(number, lot):
    s = ParkingSpace.objects.get_or_create(number=number, parking_lot=lot)[0]
    s.save()
    return s

def add_lot(name):
    l = ParkingLot.objects.get_or_create(name=name)[0]
    l.save()
    return l

# Start execution here!
if __name__ == '__main__':
    print ("Starting parking population script...")
    populate()

