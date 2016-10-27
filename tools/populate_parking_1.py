import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string

import django
django.setup()

from parking.models import ParkingLot, ParkingSpace


def populate():
    tech_lot = add_lot('科技园停车场')
    tech_lot.longitude = 113.951192
    tech_lot.latitude = 22.539824
    tech_lot.price = '2元/小时(08:00-18:00)'
    tech_lot.address = '广东省深圳市南山区高新南七道15'
    tech_lot.city_code = 340
    tech_lot.parking_space_total = 400
    tech_lot.save()

    add_space(number='100001', lot=tech_lot)
    add_space(number='100002', lot=tech_lot)
    add_space(number='100003', lot=tech_lot)
    add_space(number='100004', lot=tech_lot)

    univ_lot = add_lot('大学城停车场')
    univ_lot.longitude = 113.974889
    univ_lot.latitude = 22.594236
    univ_lot.price = '4元/小时(08:00-18:00)'
    univ_lot.address = '广东省深圳市南山区校园路'
    univ_lot.city_code = 340
    univ_lot.parking_space_total = 600
    univ_lot.save()

    add_space(number='100001', lot=univ_lot)
    add_space(number='100002', lot=univ_lot)
    add_space(number='100003', lot=univ_lot)
    add_space(number='100004', lot=univ_lot)

    bench_lot = add_lot('海岸城停车场')
    bench_lot.longitude = 113.943179
    bench_lot.latitude = 22.523915
    bench_lot.price = '6元/小时(08:00-18:00)'
    bench_lot.address = '广东省深圳市南山区文心五路33-10'
    bench_lot.city_code = 340
    bench_lot.parking_space_total = 800
    bench_lot.save()

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

