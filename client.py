import requests
import base64
import subprocess
from sys import argv
import re



def get_localaddr():
    # определение адреса компа в локальной сети (с помощью утилиты командной строки ifconfig из пакета net-tools) 
    out, err = subprocess.Popen('ifconfig', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    addr_list = re.findall(r'inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', out.decode())
    for addr in addr_list:
        if addr[:3] == '192' or addr[:3] == '172':
            return addr
    return '127.0.0.1'

try:
    host, port = argv[1].split(':')
except:
    host = get_localaddr()
    port = 5000

auth = base64.b64encode('test_serv:task_4'.encode())
headers = {'Authorization' : "Basic " + auth.decode()}

try:
    response = requests.get('http://' + host + ':' + str(port), verify=False, allow_redirects=True)
    response = response.json()
    print(response)

    for i in range(100):
        response = requests.post('http://' + host + ':' + str(port), json={'text' : f'Iteration-{i}'}, headers=headers, verify=False, allow_redirects=True)
        response = response.json()
        while True:
            if response.get('text') == 'ok':
                break
    print('all messages sent')
except:
    print('Не удалось подключиться к http://' + host + ':' + str(port))
