#!/usr/bin/python
#-*- coding:utf-8 -*-
import sys
import socket, logging
import select, errno
import json
import rsa
import base64
import requests
import hashlib
import urllib

from collections import OrderedDict

def sig_verify(data, key):
    # load public key
    #with open('demo_pri_key.pem', 'rb') as private_file:
    #    pri_data = private_file.read()

    #with open('1601210001_pub_key.pem', 'rb') as public_file:
    #    pub_data = public_file.read()

    #pri_key = rsa.PrivateKey.load_pkcs1(pri_data)
    #print(key)
    #print(key.encode('utf-8'))

    #key_from_file = rsa.PublicKey.load_pkcs1(pub_data)
    #print(pub_data)

    pub_key = rsa.PublicKey.load_pkcs1(key.encode('utf-8'))
    # extract msg and signature
    sig_start = data.find('"sign"')
    sig_value_start = data.find('"', sig_start+6)
    sig_end = data.find('"', sig_start+8)
    #info_end = data[:sig_start].rfind('"')
    #info = data[:info_end+1] + data[sig_end+1:]

    info_end = data[:sig_start].rfind(',')
    info = data[:info_end] + data[sig_end+1:]
    content = json.loads(data)
    sig_value = data[sig_value_start+1:sig_end]

    sig = base64.b64decode(sig_value.encode('utf-8'))
    #sig = base64.b64decode(content['sign'])#.encode('utf-8')

    #print(info)
    #print(sig)
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

def calc_md5(msg, entrance):
    msg = OrderedDict(sorted(msg.items()))
    s = ''
    for (k,v) in msg.items():
        s += k
        s += '='
        s += str(v)

        sch = str(v)
        s_url = ''
        # url encode
        for i in range(0, len(sch)):
            # chinese character
            if sch[i] >= u'\u4e00' and sch[i] <= u'\u9fa5':
                s_url += urllib.parse.quote_plus(sch[i]).lower()
            else:
                s_url += sch[i]

        if k == 'paytime':
            s_url = urllib.parse.quote_plus(str(v)).lower()
        #s += urllib.parse.quote_plus(str(v)).lower()
        #s += s_url
        s += '&'
    s = s[:-1]
    s += str(entrance)

    #print('Input string to md5[%s]' % s)
    m = hashlib.md5()
    m.update(s.encode('gbk'))
    #m.update(s.encode('utf-8'))
    ret = m.hexdigest()

    #print(ret)
    return(ret)


