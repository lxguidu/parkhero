#!/usr/bin/python
#-*- coding:utf-8 -*-
import sys
import socket
import logging, logging.handlers
import select, errno
import json
import rsa
import base64
import requests
import hashlib

from collections import OrderedDict
from json import JSONEncoder

from verification_tools import sig_verify, calc_md5
#from parkhero.conf import BASE_URL

logger = logging.getLogger("event_process")
SERVER_IP = "120.24.249.69"
BASE_URL="http://"+SERVER_IP+"/parkhero/"
back_end = BASE_URL+"v0.1/"
parking_url = back_end + 'parking/'
billing_url = back_end + 'billing/'
operation_url = back_end + 'operation/'

LOG_FILE = "../log/event_process.log"

logger.setLevel(logging.DEBUG)

fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 20*1024*1024, backupCount = 100)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def ingress(data, ip_address):
    identifier = int.from_bytes(data[0:8], byteorder='little', signed=False)
    body_length = int.from_bytes(data[8:16], byteorder='little', signed=False)

    try:
        body = data[16:].decode('gbk')#('utf-8')
        logger.info('Decoding msg from[%d][%s]' % (identifier,ip_address))
    except Exception as e:
        logger.error(data)
        logger.error('[%d][%s][%s]' % (identifier,ip_address,str(e)))
        return False, e

    #body2 = body.encode('utf-8')
    #body = body2.decode('utf-8')

    logger.debug(data)

    result = ''.encode('utf-8')

    if body_length == len(data[16:]):
        ret = True
    else:
        ret = False

    if ret:
        # connection accepted
        if body == 'contact':
            logger.info("Msg from parking lot[%d][%s]: connected." % (identifier,ip_address))
            content = {}
            print("Msg from parking lot[%d]: connected." % identifier)
            headers = {'application': 'json; charset=UTF-8'}
            content['identifier'] = identifier
            content['ip_address'] = ip_address

            try:
                response = requests.post(operation_url + 'parkinglot_connected/', headers=headers, json=content)
            except Exception as e:
                logger.error('Msg from server: parking lot[%d][%s], info[%s]' % (identifier,ip_address,str(e)))
            return ret, ''.encode('utf-8')

        else:
            # get public key
            try:
                response = requests.get(parking_url + 'get_public_key/?identifier=' + str(identifier))#, headers=headers, json=data)
                logger.info('Msg to server: parking lot[%d][%s] requests public key' % (identifier,ip_address))
            except Exception as e:
                logger.error('Msg from server: parking lot[%d][%s], info[%s]' % (identifier,ip_address,str(e)))
                return False, 'Socket error: can NOT get public key.'.encode('utf-8')

            if response.status_code == 200:
                data = response.json()
                pub_key = data['key']
            else:
                logger.error('Can NOT get public key from server: parking lot[%d][%s]' % (identifier,ip_address))
                return False, 'Identifier not correct: can NOT get public key.'.encode('utf-8')

            # verify signature
            if not sig_verify(body, pub_key):
                logger.error("Msg from parking lot[%d][%s]: verification failed." % (identifier,ip_address))
                return False, 'verification_failed'.encode('utf-8')

            logger.info("Msg from parking lot[%d][%s]: verified." % (identifier,ip_address))

            content = json.loads(body)
            #print(content)
            action = content['action']
            content['identifier'] = identifier
            logger.info("Msg from parking lot[%d][%s]: action[%s]." % (identifier,ip_address,content['action']))
            if action in ['in','out','pay','onlinepay','paytimeout','monthcard','cardtype','refreshprice']:
                result = {
                    'in': lambda x: action_in(x),
                    'out': lambda x: action_out(x),
                    'pay': lambda x: action_pay(x),
                    'onlinepay': lambda x: action_onlinepay(x),
                    'paytimeout': lambda x: action_paytimeout(x),
                    'monthcard': lambda x: action_monthcard(x),
                    'cardtype': lambda x: action_cardtype(x),
                    'refreshprice': lambda x: action_refreshprice(x),
                }[action](content)
            else:
                logger.error('Unknow action[%s][%s]' % (action,ip_address))
                return False, 'Unknow action'
    #print(result)

    return ret, result

def action_in(data):
    #print(data['carno'])
    logger.info('Msg from parking lot[%d]: vehicle in[%s]' % (data['identifier'], data['carno']))
    headers = {'application': 'json; charset=UTF-8'}

    errno = 0 # no exception

    try:
        response = requests.post(parking_url + 'in/', headers=headers, json=data)
        logger.info('Msg from server: parking lot[%d], status code[%d]' % (data['identifier'], response.status_code))
    except Exception as e:
        logger.error('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], str(e)))
        errno = 1

    # return message to client
    ack_msg = OrderedDict()
    ack_msg['action'] = data['action']

    if errno == 0 and  response.status_code == 200:
            ack_msg['success'] = 1
    else:
        #print('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], response.json()))
        ack_msg['success'] = 0

    ack_msg['timestamp'] = data['timestamp']
    ack_msg['notice_id'] = data['notice_id']

    md5_sum = calc_md5(ack_msg, data['identifier'])

    ack_msg['sign'] = md5_sum
    #print(json.dumps(ack_msg))

    del ack_msg['timestamp']

    #print(json.dumps(ack_msg))
    #ack_msg[''] =

    body = json.dumps(ack_msg).encode('utf-8')
    header = data['identifier'].to_bytes(8, byteorder='little')
    header += len(body).to_bytes(8, byteorder='little')

    return header+body

def action_out(data):
    logger.info('Msg from parking lot[%d]: vehicle out[%s]' % (data['identifier'], data['carno']))
    headers = {'application': 'json; charset=UTF-8'}

    errno = 0

    try:
        response = requests.post(parking_url + 'out/', headers=headers, json=data)
        logger.info('Msg from server: parking lot[%d], status code[%d]' % (data['identifier'], response.status_code))
    except Exception as e:
        logger.error('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], str(e)))
        errno = 1

    # return message to client
    ack_msg = OrderedDict()
    ack_msg['action'] = data['action']

    if errno == 0 and  response.status_code == 200:
            ack_msg['success'] = 1
    else:
        #print('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], response.json()))
        ack_msg['success'] = 0

    ack_msg['timestamp'] = data['timestamp']
    ack_msg['notice_id'] = data['notice_id']

    md5_sum = calc_md5(ack_msg, data['identifier'])

    ack_msg['sign'] = md5_sum
    #print(json.dumps(ack_msg))

    del ack_msg['timestamp']

    #print(json.dumps(ack_msg))

    body = json.dumps(ack_msg).encode('utf-8')
    #body_length = len(body)
    header = data['identifier'].to_bytes(8, byteorder='little')
    #body_lenth_bytes = body_length.to_bytes(8, byteorder='little')

    #header_total = header + body_lenth_bytes
    header += len(body).to_bytes(8, byteorder='little')

    return header+body

def action_pay(data):
    logger.info('Msg from parking lot[%d]: payment[%s]' % (data['identifier'], data['carno']))
    headers = {'application': 'json; charset=UTF-8'}

    errno = 0

    try:
        response = requests.post(billing_url + 'pay_offline/', headers=headers, json=data)
        logger.info('Msg from server: parking lot[%d], status code[%d]' % (data['identifier'], response.status_code))
        logger.info(response.text)
    except Exception as e:
        logger.error('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], str(e)))
        errno = 1

    # return message to client
    ack_msg = OrderedDict()
    ack_msg['action'] = data['action']

    if errno == 0 and  response.status_code == 200:
        ack_msg['success'] = 1
    else:        
        ack_msg['success'] = 0

    ack_msg['timestamp'] = data['timestamp']
    ack_msg['notice_id'] = data['notice_id']

    md5_sum = calc_md5(ack_msg, data['identifier'])

    ack_msg['sign'] = md5_sum

    del ack_msg['timestamp']

    body = json.dumps(ack_msg).encode('utf-8')
    header = data['identifier'].to_bytes(8, byteorder='little')
    header += len(body).to_bytes(8, byteorder='little')

    return header+body


def action_onlinepay(data):
    #logger.info('Msg from parking lot[%d]: onlinepay[%s]' % (data['identifier'], data['carno']))
    logger.info(data)
    headers = {'application': 'json; charset=UTF-8'}

    errno = 0


def action_paytimeout(data):
    logger.info('Msg from parking lot[%d]: timeout payment[%s]' % (data['identifier'], data['carno']))
    headers = {'application': 'json; charset=UTF-8'}

    errno = 0

    try:
        response = requests.post(billing_url + 'pay_offline/', headers=headers, json=data)
        logger.info('Msg from server: parking lot[%d], status code[%d]' % (data['identifier'], response.status_code))

        #print(response.content)
    except Exception as e:
        logger.error('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], str(e)))
        errno = 1

    # return message to client
    ack_msg = OrderedDict()
    ack_msg['action'] = data['action']

    if errno == 0 and  response.status_code == 200:
            ack_msg['success'] = 1
    else:
        #print('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], response.json()))
        ack_msg['success'] = 0

    ack_msg['timestamp'] = data['timestamp']
    ack_msg['notice_id'] = data['notice_id']

    md5_sum = calc_md5(ack_msg, data['identifier'])

    ack_msg['sign'] = md5_sum

    del ack_msg['timestamp']

    body = json.dumps(ack_msg).encode('utf-8')
    header = data['identifier'].to_bytes(8, byteorder='little')
    header += len(body).to_bytes(8, byteorder='little')

    return header+body

    pass

def action_monthcard(data):
    logger.info('Msg from parking lot[%d]: monthly card payment[%s]' % (data['identifier'], data['carno']))
    headers = {'application': 'json; charset=UTF-8'}

    errno = 0

    try:
        response = requests.post(billing_url + 'monthly_card/', headers=headers, json=data)
        logger.info('Msg from server: parking lot[%d], status code[%d]' % (data['identifier'], response.status_code))
    except Exception as e:
        logger.error('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], str(e)))
        errno = 1

    # return message to client
    ack_msg = OrderedDict()
    ack_msg['action'] = data['action']

    if errno == 0 and  response.status_code == 200:
            ack_msg['success'] = 1
    else:
        #print('Msg from server: parking lot[%d], info[%s]' % (data['identifier'], response.json()))
        ack_msg['success'] = 0

    ack_msg['timestamp'] = data['timestamp']
    ack_msg['notice_id'] = data['notice_id']

    md5_sum = calc_md5(ack_msg, data['identifier'])

    ack_msg['sign'] = md5_sum

    del ack_msg['timestamp']

    body = json.dumps(ack_msg).encode('utf-8')
    header = data['identifier'].to_bytes(8, byteorder='little')
    #body_lenth_bytes = body_length.to_bytes(8, byteorder='little')

    #header_total = header + body_lenth_bytes
    header += len(body).to_bytes(8, byteorder='little')

    return header+body

def action_cardtype(data):
    pass

def action_refreshprice(data):
    pass

def _sig_verify(data):
    # load public key
    with open('demo_pri_key.pem', 'rb') as private_file:
        pri_data = private_file.read()

    with open('demo_pub_key.pem', 'rb') as public_file:
        pub_data = public_file.read()

    pri_key = rsa.PrivateKey.load_pkcs1(pri_data)
    pub_key = rsa.PublicKey.load_pkcs1(pub_data)

    # extract msg and signature
    sig_start = data.find('"sign"')
    sig_value_start = data.find('"', sig_start+6)
    sig_end = data.find('"', sig_start+8)
    info_end = data[:sig_start].rfind('"')

    info = data[:info_end+1] + data[sig_end+1:]
    content = json.loads(data)
    sig_value = data[sig_value_start+1:sig_end]

    sig = base64.b64decode(sig_value.encode('utf-8'))
    #sig = base64.b64decode(content['sign'])#.encode('utf-8')

    #print(info)
    #sig = base64.b64encode(rsa.sign(info.encode('utf-8'), pri_key, 'SHA-1'))

    try:
        #result = rsa.verify(info.encode('utf-8'), sig, pub_key)
        result = rsa.verify(info.encode('gbk'), sig, pub_key)
        #print('Signature veirified.')
        #result = rsa.verify(msg, sig2, pri_key)
    except:
        result = False
        #print('Verification failed')

    return result

def _cacl_md5(msg, entrance):
    msg = OrderedDict(sorted(msg.items()))
    s = ''
    for (k,v) in msg.items():
        s += k
        s += '='
        s += str(v)
        s += '&'
    s = s[:-1]
    s += str(entrance)

    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    ret = m.hexdigest()

    return(ret)