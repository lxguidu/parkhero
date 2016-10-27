# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-28 03:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_auto_20160221_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrePayNotifyAliPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_no', models.CharField(max_length=32)),
                ('trade_status', models.CharField(max_length=20)),
                ('buyer_email', models.CharField(max_length=50)),
                ('buyer_id', models.CharField(max_length=50)),
                ('seller_id', models.CharField(max_length=50)),
                ('seller_email', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=50)),
                ('body', models.CharField(max_length=50)),
                ('quantity', models.CharField(max_length=5)),
                ('price', models.CharField(max_length=13)),
                ('total_fee', models.CharField(max_length=13)),
                ('discount', models.CharField(max_length=13)),
                ('is_total_fee_adjust', models.CharField(max_length=4)),
                ('use_coupon', models.CharField(max_length=4)),
                ('payment_type', models.CharField(max_length=4)),
                ('gmt_create', models.CharField(max_length=30)),
                ('gmt_payment', models.CharField(max_length=30)),
                ('notify_time', models.CharField(max_length=30)),
                ('notify_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PrePayNotifyWeChatPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=32)),
                ('mch_id', models.CharField(max_length=32)),
                ('open_id', models.CharField(max_length=32)),
                ('transaction_id', models.CharField(max_length=32)),
                ('total_fee', models.CharField(max_length=13)),
                ('trade_type', models.CharField(max_length=20)),
                ('fee_type', models.CharField(max_length=10)),
                ('bank_type', models.CharField(max_length=10)),
                ('cash_fee', models.CharField(max_length=13)),
                ('is_subscribe', models.CharField(max_length=4)),
                ('time_end', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='PrePayOrderAliPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner', models.CharField(max_length=32)),
                ('seller_id', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=50)),
                ('body', models.CharField(max_length=50)),
                ('total_fee', models.CharField(max_length=13)),
                ('payment_type', models.CharField(max_length=4)),
                ('service', models.CharField(max_length=80)),
                ('it_b_pay', models.CharField(max_length=5)),
                ('notify_url', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='PrePayOrderWeChatPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=32)),
                ('mch_id', models.CharField(max_length=32)),
                ('body', models.CharField(max_length=50)),
                ('total_fee', models.CharField(max_length=13)),
                ('spbill_create_ip', models.CharField(max_length=50)),
                ('notify_url', models.CharField(max_length=80)),
                ('trade_type', models.CharField(max_length=20)),
                ('response_app_id', models.CharField(max_length=32)),
                ('response_mch_id', models.CharField(max_length=32)),
                ('responsetrade_type', models.CharField(max_length=20)),
                ('prepay_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='app_id',
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='mch_id',
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='open_id',
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='prepay_id',
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='time_end',
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='trade_no',
        ),
        migrations.RemoveField(
            model_name='prepayorder',
            name='transaction_id',
        ),
        migrations.AddField(
            model_name='prepayorder',
            name='out_trade_no',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='prepayorder',
            name='payment_channel',
            field=models.CharField(max_length=10),
        ),
        migrations.AddField(
            model_name='prepayorderwechatpay',
            name='prepay_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PrePayOrder'),
        ),
        migrations.AddField(
            model_name='prepayorderalipay',
            name='prepay_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PrePayOrder'),
        ),
        migrations.AddField(
            model_name='prepaynotifywechatpay',
            name='prepay_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PrePayOrder'),
        ),
        migrations.AddField(
            model_name='prepaynotifyalipay',
            name='prepay_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PrePayOrder'),
        ),
    ]