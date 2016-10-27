import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkhero.settings')

import string
import rsa

from subprocess import call

import django
django.setup()

from parking.models import ParkingLot, ParkingSpace


def add_identifier():
    # get the number of parking lot
    lots = ParkingLot.objects.all()
    total = lots.count()
    print(total)

    for lot in lots:
        # generate identifier
        if lot.identifier>1608060000:
             print(lot.identifier)
        else:
             continue
        identifier = lot.identifier
        key_name = str(identifier)
        print('key name[%s], identifier[%d]' % (key_name,identifier))
        print('parking lot[%s]' % lot.name)
        #lot.identifier = identifier

        # generate key pair
        generate_key(key_name)

        # read key
        with open(key_name + '_pri_key_pkcs8.pem', 'rb') as private_file:
            pri_data = private_file.read()
        with open(key_name + '_pub_key.pem', 'rb') as public_file:
            pub_data = public_file.read()

        # write to database
        lot.private_key = pri_data
        lot.public_key = pub_data

        lot.save()

    return lot


def generate_key(key_name):
    # name of the keys
    pri_key_name = key_name + '_pri_key.pem'
    pri_key_pkcs8_name = key_name + '_pri_key_pkcs8.pem'
    pub_key_name = key_name + '_pub_key.pem'

    # private key
    call(['openssl', 'genrsa', '-out', pri_key_name, '1024'])

    # private key in pkcs8
    call(['openssl', 'pkcs8', '-topk8',
          '-in', pri_key_name,
          '-out', pri_key_pkcs8_name,
          '-nocrypt'])

    # public key
    call(['openssl', 'rsa',
          '-in', pri_key_name,
          '-RSAPublicKey_out',
          '-out', pub_key_name])

# Start execution here!
if __name__ == '__main__':
    print ("Starting parking lot identifier and rsa key population script...")
    #populate()
    add_identifier()


