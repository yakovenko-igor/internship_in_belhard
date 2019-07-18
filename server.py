#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
from sys import argv
import subprocess
import re
import logging
from logging.handlers import RotatingFileHandler
from socket import socket
from flask import Flask, request, jsonify, make_response
from flask.logging import default_handler
from gevent.pywsgi import WSGIServer
from flask_httpauth import HTTPBasicAuth



# создаем папку для логов, если она еще не создана
if not os.path.exists('log'):
    os.makedirs('log')

mylogger = logging.getLogger()
mylogger.setLevel(logging.DEBUG)

# логи будут записываться в файлы в папке log, а так же выводиться в консоль

rfh = RotatingFileHandler(filename='log/mylog.log', maxBytes=16777216, backupCount=5) # ротация логов, 5 log-файлов по 16 МБ
rfh.setLevel(logging.DEBUG)
rfh.setFormatter(logging.Formatter('%(levelname)-8s | %(asctime)s | %(message)s'))

console = logging.StreamHandler() # вывод логов в консоль
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('%(levelname)-8s | %(asctime)s | %(message)s'))

mylogger.addHandler(console)
mylogger.addHandler(rfh)


host = '127.0.0.1'
port = 5000
app = Flask(__name__)
auth = HTTPBasicAuth()
users = {
    'test_serv' : 'task_4'
}
max_data_length = 16777216 # 16 MB

def limit_data_length(f):
    def wrap():
        if request.content_length > max_data_length:
            return make_response(jsonify({'error': 'Maximum data transfer size exceeded, allowed only until {:.2f} kB.'.format(max_data_length/1024)}), 413)
        return f()
    return wrap

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method Not Allowed'}), 405)

@app.errorhandler(406)
def not_acceptable(error):
    return make_response(jsonify({'error': 'Not Acceptable'}), 406)

@app.errorhandler(415)
def unsupported_media_type(error):
    return make_response(jsonify({'error': 'Unsupported Media Type'}), 415)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)

@app.route("/", methods=['POST'])
@auth.login_required
@limit_data_length
def post_message():
    message = request.json.get('text')
    if message:
        mylogger.info(request.remote_addr + ':' + str(request.environ.get('REMOTE_PORT')) + ' | ' + message)
        return jsonify({'text': 'ok'})

@app.route("/", methods=['GET'])
def get_info():
        return jsonify({'text': "Сервер был написан в рамках задания во время стажировки в БелХард. Сервер может принимать от клиентов два вида запросов: GET-запрос на '/' и POST-запрос на '/'. При GET-запросе сервер возвращает json формата {'text' : '[информация о сервере]'}. При POST-запросе клиент может передать строку, для этого он должен передать json вида {'text' : '[передаваемая информация]'}, сервер записывает полученную информацию в log и возвращает клиенту json вида {'text' : 'ok'}, уведомляющий клиента о том, что информация получена. Ограничение на размер принимаемых данных в теле запроса равно 16 МБ."})

def get_localaddr():
    # определение адреса компа в локальной сети (с помощью утилиты командной строки ifconfig из пакета net-tools) 
    out, err = subprocess.Popen('ifconfig', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    addr_list = re.findall(r'inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', out.decode())
    for addr in addr_list:
        if addr[:3] == '192' or addr[:3] == '172':
            return addr
    return '127.0.0.1'

def run_server(host, port, https=False, test_flask=False):
    if host == 'localaddr':
        host = get_localaddr()
    if port == 0:
        sock = socket()
        sock.bind((host, 0))
        port = sock.getsockname()[1]
        sock.close()
    try:
        if test_flask:
            if https:
                app.run(host=host, port=port, debug=False, threaded=True, ssl_context=('cert.pem', 'key.pem'))
                # threaded=True - обрабатывает каждый запрос в отдельном потоке
            else:
                app.run(host=host, port=port, debug=False, threaded=True) 
        else:
            mylogger.info('Запуск WSGI-сервера на адресе ' + host + ':' + str(port))
            if https:
                myWSGIserver = WSGIServer((host, port), app, log=mylogger, error_log=mylogger, keyfile='key.pem', certfile='cert.pem')
            else:
                myWSGIserver = WSGIServer((host, port), app, log=mylogger, error_log=mylogger)
            myWSGIserver.serve_forever()
    except KeyboardInterrupt:
        mylogger.info('Сервер остановлен')
    except OSError:
        mylogger.error('Не удалось запустить сервер на адресе ' + host + ':' + str(port) + ', адрес недоступен')


if len(argv) > 1:
    if argv[1] == '-s':
        if len(argv) > 2:
            if argv[2] == '-d':
                if len(argv) > 3:
                    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', argv[3]) or re.search(r'localaddr:\d+', argv[3]):
                        host, port = argv[3].split(':')
                        port = int(port)
                        run_server(host=host, port=port, https=True, test_flask=True)
                    else:
                        print('[Error] Неизвестный аргумент: "' + argv[3] + '"')
                else:
                    run_server(host=host, port=port, https=True, test_flask=True)
            elif re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', argv[2]) or re.search(r'localaddr:\d+', argv[2]):
                host, port = argv[2].split(':')
                port = int(port)
                run_server(host=host, port=port, https=True)
            else:
                print('[Error] Неизвестный аргумент: "' + argv[2] + '"')
        else:
            host = get_localaddr()
            run_server(host=host, port=port, https=True)
    elif argv[1] == '-d':
        if len(argv) > 2:
            if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', argv[2]) or re.search(r'localaddr:\d+', argv[2]):
                host, port = argv[2].split(':')
                port = int(port)
                run_server(host=host, port=port, test_flask=True)
            else:
                print('[Error] Неизвестный аргумент: "' + argv[2] + '"')
        else:
            run_server(host=host, port=port, test_flask=True)
    elif re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', argv[1]) or re.search(r'localaddr:\d+', argv[1]):
        host, port = argv[1].split(':')
        port = int(port)
        run_server(host=host, port=port)
    else:
        print('[Error] Неизвестный аргумент: "' + argv[1] + '"')
else:
    host = get_localaddr()
    run_server(host=host, port=port)