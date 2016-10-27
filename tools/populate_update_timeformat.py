import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string

import django
django.setup()

from parking.models import ParkingLot, ParkingSpace, VehicleIn, VehicleOut
from billing.models import OfflinePayment, MonthlyCardPayment

def v_in_format():
    # vehicle in records
    v_ins = VehicleIn.objects.filter(in_time__contains='/')
    for v in v_ins:
        print(v.plate_number,v.in_time)
        print('---- update time format ----')
        in_time = v.in_time.replace('/', '-')
        v.in_time = in_time
        v.save()

def v_out_format():
    # vehicle in records
    v_outs = VehicleOut.objects.filter(out_time__contains='/')
    for v in v_outs:
        print(v.plate_number,v.out_time)
        print('---- update time format ----')
        out_time = v.out_time.replace('/', '-')
        v.out_time = out_time
        v.save()

def off_pay_format():
    # vehicle in records
    pays = OfflinePayment.objects.filter(payment_time__contains='/')
    for pay in pays:
        print(pay.plate_number,pay.payment_time)
        print('---- update time format ----')
        payment_time = pay.payment_time.replace('/', '-')
        pay.payment_time = payment_time
        pay.save()

def month_pay_format():
    # vehicle in records
    pays = OfflinePayment.objects.filter(payment_time__contains='/')
    for pay in pays:
        print(pay.plate_number,pay.payment_time)
        print('---- update time format ----')
        payment_time = pay.payment_time.replace('/', '-')
        pay.payment_time = payment_time
        pay.save()

# Start execution here!
if __name__ == '__main__':
    print ("Starting time format update population script...")
    #v_in_format()
    #v_out_format()
    #off_pay_format()
    month_pay_format()

