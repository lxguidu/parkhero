import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string

import django
django.setup()

from parking.models import ParkingLot, ParkingSpace


def add_lots():
    f = open('parking_lots_utf8_20160511.txt', 'r')
    content = f.read().splitlines()

    identifier = 1605110001

    for line in content:
        #print(line)
        items = line.split('\t')
        print(items)
        name = items[0]
        l = ParkingLot.objects.get_or_create(name=name)[0]

        l.address = items[1]

        if items[2] != '':
            l.parking_space_total = int(items[2])
        else:
            l.parking_space_total = 888

        if items[3] != '':
            l.price = items[3]
        else:
            l.price = '1-12小时5元 12-24小时10元'

        l.longitude = items[4]

        l.latitude = items[5]

        l.city_code = 158

        l.identifier = identifier
        identifier = identifier + 1
        l.type = '封闭'

        print(l)
        l.save()

# Start execution here!
if __name__ == '__main__':
    print ("Starting parking population script...")
    add_lots()
    #add_identifier()


