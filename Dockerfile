FROM ubuntu:18.04

# Установка пакетов для Ubuntu
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3.6 \
    python3-pip \
    git \
    net-tools \
    locales \
    tzdata

# Установка модулей для Python3
RUN pip3 install --upgrade pip
RUN pip3 install \
    flask==1.0.3 \
    flask-httpauth==3.2.4 \
    gevent==1.4.0 \
    requests==2.22.0

# Установка часового пояса
ENV TZ=Europe/Minsk
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Изменение локализации для вывода кириллицы в терминале
RUN locale-gen ru_RU.UTF-8
ENV LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8

# Копирование файлов проекта
COPY . /task4
WORKDIR /task4

# Очистка кеша
RUN apt-get -y autoremove && \
    apt-get -y autoclean && \
    apt-get -y clean

CMD ["python3", "server.py"]