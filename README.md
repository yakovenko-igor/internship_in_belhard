# Клиент-сервер

Данный проект выполнен в рамках задания полученного во время стажировки в БелХард. Он состоит из клиента и сервера.

Для запуска сервера необходимо запустить ```python3 server.py```, для запуска клиента - ```python3 client.py```.

## Зависимости

1. Для Ubuntu: python3.6, python3-pip, git, net-tools.
2. Для Python3: flask (=1.0.3), flask-httpauth (=3.2.4), gevent (=1.4.0), requests (=2.22.0).

## Сервер

Сервер соответствует архитектуре REST, поддерживает https с сертификатами от openssl. Сервер может принимать от клиентов два вида запросов: GET-запрос на `/` и POST-запрос на `/`. При GET-запросе сервер возвращает json формата `{'text' : '[информация о сервере]'}`. При POST-запросе клиент может передать строку, для этого он должен передать json вида `{'text' : '[передаваемая информация]'}`, сервер записывает полученную информацию в log и возвращает клиенту json вида `{'text' : 'ok'}`, уведомляющий клиента о том, что информация получена. Ограничение на размер принимаемых данных в теле запроса равно 16 МБ. Максимальный размер одного лог файла - 16МБ, количество файлов - 5, log дублируется в терминал. Формат логов: `уровень | дата_и_время | адрес_клиента | сообщение`. Так же в log записываются действия сервера и другая информация, в таком случае формат логов: `уровень | дата_и_время | информация`.

Сервер имеет базовую http-авторизацию. Для успешной отправки POST-запроса в него необходимо добавить заголовок, содержащий логин:пароль, закодированный с помощью `base64` (логин: `test_serv`, пароль: `task_4`). Пример на python:

```python
import requests
import base64

auth = base64.b64encode('test_serv:task_4'.encode())
headers = {'Authorization' : "Basic " + auth.decode()}
```

Сервер можно запускать с агрументами командной строки, которые имеют следующую структуру: `[ключ(-и)] [адрес:порт]`. Список возможных комбинаций аргументов командной строки и их описание:

без аргументов - запуск WSGI сервера с автоопределением адреса машины в локальной сети и портом `5000`.
Например: ```python3 server.py```

`host:port` - запуск WSGI сервера на указанном `host` и `port`.
Например: ```python3 server.py 192.168.2.102:5000```

`-d` - запуск тестового Flask сервера на `127.0.0.1:5000`.
Например: ```python3 server.py -d```

`-d` host:port - запуск тестового Flask сервера на указанном `host` и `port`.
Например: ```python3 server.py -d 192.168.2.102:5000```

`-d localaddr:port` - запуск тестового Flask сервера с автоопределением адреса машины в локальной сети и портом `port`.
Например: ```python3 server.py -d localaddr:5000```

`-s` - запуск WSGI сервера с поддержкой https, автоопределением адреса машины в локальной сети и портом `5000`.
Например: ```python3 server.py -s```

`-s host:port` - запуск WSGI сервера с поддержкой https на указанном `host` и `port`.
Например: ```python3 server.py -s 192.168.2.102:5000```

`-s -d` - запуск тестового Flask сервера с поддержкой https на `127.0.0.1:5000`.
Например: ```python3 server.py -s -d```

`-s -d host:port` - запуск тестового Flask сервера с поддержкой https на указанном `host` и `port`.
Например: ```python3 server.py -s -d 192.168.2.102:5000```

`-s -d localaddr:port` - запуск тестового Flask сервера с поддержкой https, автоопределением адреса машины в локальной сети и портом `port`.
Например: ```python3 server.py -s -d localaddr:5000```

При указании в `host:port` или `localaddr:port` порт 0 (например: ```python3 server.py -d localaddr:0```) сервер сам находит любой свободный порт.

## Клиент

Клиент посылает GET-запрос на `/`, а затем запускает цикл на 100 итераций, где в каждой итерации на сервер посылается POST-запрос на `/`, в котором передается json вида `{'text' : 'Iteration [номер итерации]'}`. Так же GET-запрос на `/` можно послать просто подключившись к серверу через браузер.

Клиент можно запускать с агрументами командной строки, которые имеют следующую структуру: `[адрес:порт]`. Список возможных комбинаций аргументов командной строки и их описание:

без аргументов - запуск с автоопределением адреса машины в локальной сети и портом `5000`.
Например: ```python3 client.py```

`host:port` - запуск с подключением к указанному `host` и `port`.
Например: ```python3 client.py 192.168.2.102:5000```

## Docker-образ с RESTful сервером

В проекте содержится Dockerfile, который позволяет собрать docker образ на основе данного проекта.

Для сборки образа необходимо перейти в терминале в папку с проектом и выполнить (`-t` — запуск терминала, `.` — директория, из которой вызывается docker build (точка — значит в текущей директории находятся все файлы для образа), `task5:0.1` — метка образа и его версия):

```bash
sudo docker build -t task5:0.1 .
```

После успешного выполнения данной операции вы можете вывести список имеющихся образов, выполнив:

```bash
sudo docker images
```

В полученном списке вы увидите наш образ — `task5:0.1`.

Теперь вы можете запустить этот образ (`-t` — запуск терминала, `-i` — интерактивный режим, `--rm` — удалить контейнер после завершения его работы, `-p 5000:5000` — пробросить все подключения на порт 5000 к машине-хосту в контейнер на порт 5000 (вы так же можете явно указать другой адрес, к которому нужно будет подключиться извне, например: `-p 127.0.0.1:5000:5000`)):

```bash
sudo docker run -ti --rm -p 5000:5000 task5:0.1
```

В результате запустится RESTful сервер на вашем локальном адресе и порте `5000` и можно к нему обращаться по указанному в терминале адресу (если вы не указали другой при запуске образа).
