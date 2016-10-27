#-*- coding: utf-8 -*-
STATUS_CODE = {
    # parkhero
    # - 系统级状态码       
    "success"       : 0,
    "unknown_err"   : 10000, # 未知原因错误
    "errparam"      : 10001, # 参数错误
    "lostparam"     : 10002, # 缺少必要参数
    "database_err"  : 10003, # 数据库错误
    "network_err"   : 10004, # 网络错误
    "need_login"    : 10005, # 需要登录才能进行下一步操作
    "non_right"     : 10006, # 没有权限      

    # - 账号模块
    "verify_code_expired"   : 20000, # 验证码过期        
    "verify_code_invalid"   : 20001, # 验证码无效
    "verify_code_wait"      : 20002, # 请稍等验证码下发
    "phone_num_registed"    : 20003, # 该手机号码已经被注册
    "phone_num_notregisted" : 20004, # 该手机号码未被注册
    "user_no_profile"       : 20005, # 该用户没有配置数据
    "pay_passwd_err"        : 20006, # 支付密码错误
    "pay_passwd_noexist"    : 20007, # 没有支付密码
    "trade_num_noexist"     : 20008, # 该订单号不存在
    "user_passwd_err"       : 20009, # 用户名密码错误
    "non_administrator"     : 20010, # 不是管理员
    "non_such_user"         : 20011, # 没有该用户
    "non_such_role"         : 20012, # 没有该角色
    "username_exists"       : 20013, # 用户名已经存在
    "non_operator"          : 20014, # 不是操作员
    "non_auth_del_group"    : 20015, # 没有权限删除用户组  
    "groupname_exists"      : 20016, # 该用户组已经存在    

    # - 支付模块(billing)

    # - web后台模块(operation)
    "non_valid_packname"    : 40001, # 不是有效地app包名
    "non_app_release"       : 40002, # 没有app发布
    "non_such_parklot"      : 40003, # 没有该停车场
    "such_parklot_exist"    : 40004, # 该停车场已经存在
    "non_parklot"           : 40005, # 没有停车场
    "non_vehiclein_record"  : 40006, # 没有停车入场记录
    "non_vehicleout_record" : 40007, # 没有停车出场记录
    "non_offlinepay_record" : 40008, # 没有线下缴费记录
    "non_onlinepay_record"  : 40009, # 没有线上缴费记录

    # - 停车场模块

    # - 停车场通信模块

    # - app用户概况模块

    # - app版本模块
    "non_file_exists"       : 80001, # 文件不存在
    "non_startup_image"     : 80002, # 没有启动页面图片
    "non_index_image"       : 80003, # 没有首页页面图片
    "non_cover_image"       : 80004, # 没有封面页面图片

    # - 短信模块
}