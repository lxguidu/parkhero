#-*- coding: UTF-8 -*-  

#from CCPRestSDK import REST

from yuntongxun_sms.CCP_REST_DEMO_Python_v2_7r.SDK.CCPRestSDK import REST

import configparser

#���ʺ�
accountSid= 'aaf98f89510f639f015113202ffb0ac4';

#���ʺ�Token
accountToken= '30a84a174bd64b6f8b8b966f2a45c05f';

#Ӧ��Id
appId='aaf98f89510f639f0151132a2eae0b04';

#������ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com';

#�����˿� 
serverPort='8883';

#REST�汾��
softVersion='2013-12-26';

  # ����ģ������
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

def sendTemplateSMS(to,data,tempId):

    
    #��ʼ��REST SDK
    rest = REST(serverIP,serverPort,softVersion)
    rest.BodyType = 'json'
    rest.Iflog = False
    rest.setAccount(accountSid,accountToken)
    rest.setAppId(appId)
    
    result = rest.sendTemplateSMS(to,data,tempId)

    return result