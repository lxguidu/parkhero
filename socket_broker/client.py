import socket
import time
import logging
import pytz
import json

from datetime import date, datetime
from collections import OrderedDict

from django.db import models

from billing.models import Bill
from parking.models import VehicleIn, ParkingLot

from socket_broker.verification_tools import calc_md5

logger = logging.getLogger("network-client")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("log/network-client.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

class BrokerClient():
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 2003

        try:
            self.sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        except socket.error as msg:
            logger.error(msg)

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            logger.debug("connect to network server success")
        except socket.error as msg:
            logger.error(msg)
            return False

        return True

    def pay(self, bill):
        v_in = bill.vehicle_in
        lot = v_in.parking_lot
        #e = ParkingLot.objects.get(pk=p.entrance_id)
        identifier = lot.identifier
        logger.info('Msg from socket client: online pay[%s][%s]' % (lot.name,v_in.plate_number))

        plate_number = v_in.plate_number
        amount = bill.amount
        now = datetime.now(pytz.utc)
        time_stamp = int(time.mktime(now.timetuple()))
        print(time_stamp)
        #print(time.mktime(time_stamp.timetuple()))
        #pay_date = now.strftime('%Y-%m-%d')
        now_gmt8 = now.astimezone(pytz.timezone('Asia/Shanghai'))
        pay_time = now_gmt8.strftime('%Y-%m-%d %H:%M:%S')#date.fromtimestamp(time_stamp)
        logger.info(pay_time)

        logger.info('Msg to parking lot: online pay[%s][%s][%s][%s]' % (lot.name,plate_number,pay_time,amount))

        # message to parking lot
        msg = OrderedDict()
        msg['success'] = 1
        msg['action'] = 'onlinepay'
        msg['carno'] = plate_number# '临BK1234' # plate_number
        # a = '%.2f' % amount
        # b = float(a)
        # c = decimal.Decimal(amount).quantize(decimal.Decimal('0.1'))
        msg['paymoney'] = int(amount)
        #msg['paymoney'] = '%.1f' % amount
        msg['paytime'] = pay_time
        msg['timestamp'] = time_stamp
        msg['notice_id'] = bill.out_trade_no

        m = calc_md5(msg, identifier)

        msg['sign'] = m

        body = json.dumps(msg, ensure_ascii=False).encode('gbk')# TODO. not unicode. any adaption?
        #body = json.dumps(msg).encode('utf-8')
        logger.info(body)

        header = identifier.to_bytes(8, byteorder='little')
        header += len(body).to_bytes(8, byteorder='little')

        ret = self.sock.send(header+body)
        return ret

    def test(self):
        for i in range(1, 11):
            data = "消息: The Number is %d" % i
            print(data)
            if connFd.send(data.encode('utf-8')) != len(data.encode()):
                logger.error("send data to network server failed")
                break
            readData = connFd.recv(1024)
            print(readData.decode())
            time.sleep(1)

    def close(self):
        self.sock.close()

