# vim app.py
# -*- coding: utf-8 -*-
import os
import json
import requests
import arrow
from flask import Flask
from flask import request
app = Flask(__name__)
def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)
def makealertdata(data):
    for output in data['alerts'][:]:
        try:
            pod_name = output['labels']['pod']
        except KeyError:
            try:
                pod_name = output['labels']['pod_name']
            except KeyError:
                pod_name = 'null'
        try:
            namespace = output['labels']['namespace']
        except KeyError:
            namespace = 'null'
        try:
            message = output['annotations']['message']
        except KeyError:
            try:
                message = output['annotations']['description']
            except KeyError:
                message = 'null'
        if output['status'] == 'firing':
            status_zh = '报警'
            title = '【%s】宝安楼栋生产环境 %s 有新的报警' % (status_zh, output['labels']['alertname'])
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "## %s \n\n" %title +
                            ">**告警级别**: %s \n\n" % output['labels']['severity'] +
                            ">**告警类型**: %s \n\n" % output['labels']['alertname'] +
                            ">**告警主机**: %s \n\n" % output['labels']['instance'] +
                            ">**告警详情**: %s \n\n" % output['annotations']['summary'] +
                            ">**告警状态**: %s \n\n" % output['status'] +
                            ">**触发时间**: %s \n\n" % arrow.get(output['startsAt']).to('Asia/Shanghai').format(
                        'YYYY-MM-DD HH:mm:ss ZZ')
                }
            }
        elif output['status'] == 'resolved':
            status_zh = '恢复'
            title = '【%s】宝安楼栋生产环境 %s 有报警恢复' % (status_zh, output['labels']['alertname'])
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "## %s \n\n" %title +
                            ">**告警级别**: %s \n\n" % output['labels']['severity'] +
                            ">**告警类型**: %s \n\n" % output['labels']['alertname'] +
                            ">**告警主机**: %s \n\n" % output['labels']['instance'] +
                            ">**告警详情**: %s \n\n" % output['annotations']['summary'] +
                            ">**告警状态**: %s \n\n" % output['status'] +
                            ">**触发时间**: %s \n\n" % arrow.get(output['startsAt']).to('Asia/Shanghai').format(
                        'YYYY-MM-DD HH:mm:ss ZZ') +
                            ">**触发结束时间**: %s \n" % arrow.get(output['endsAt']).to('Asia/Shanghai').format(
                        'YYYY-MM-DD HH:mm:ss ZZ')
                }
            }
        return send_data
def send_alert(data):
  #此处获取环境变量“TOKEN”，会在docker-compose的配置文件中配置，docker-compose启动docker时向docker容器注入环境变量
    url = os.getenv('URL')
    if not url:
        print('you must set ROBOT_TOKEN env')
        return
    send_data = makealertdata(data)
    req = requests.post(url, json=send_data)
    result = req.json()
    if result['errcode'] != 0:
        print('notify dingtalk error: %s' % result['errcode'])
@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data = request.get_data()
        send_alert(bytes2json(post_data))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'
if __name__ == '__main__':
    app_port = os.getenv('PORT')
    app.run(host='0.0.0.0', port=app_port)
