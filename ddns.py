import asyncio
import os
import json
import signal
import functools
from urllib import request, error, parse


def read_config_to_env():
    config_path = '/etc/dnspod/ddnsrc'
    if os.path.isfile(config_path):
        try:
            f = open(config_path)
            for item in f:
                item = item.split('=')
                os.environ[item[0]] = item[1].split()[0]
            f.close()
        except IndexError:
            print('config error')
            exit()
        if not os.getenv('RECORD_ID'):
            record_id = get_record_id(os.getenv('DOMAIN'), os.getenv('SUB_DOMAIN'))
            os.environ['RECORD_ID'] = record_id


def check_config():
    login_token = os.getenv('LOGIN_TOKEN')
    domain = os.getenv('DOMAIN')
    sub_domain = os.getenv('SUB_DOMAIN')
    if not (login_token and domain and sub_domain):
        print('config error')
        exit()


def header():
    h = {
        'User-Agent': 'Client/0.0.1 ({})'.format(os.getenv('EMAIL', 'null@null.com'))
    }
    return h


def get_record_id(domain, sub_domain):
    url = 'https://dnsapi.cn/Record.List'
    params = parse.urlencode({
        'login_token': os.getenv('LOGIN_TOKEN'),
        'format': 'json',
        'domain': domain
    })
    req = request.Request(url=url, data=params.encode('utf-8'), method='POST', headers=header())
    resp = request.urlopen(req).read().decode()
    records = json.loads(resp).get('records', {})
    for item in records:
        if item.get('name') == sub_domain:
            return item.get('id')
    return None


def get_ip():
    url = 'http://www.httpbin.org/ip'
    try:
        resp = request.urlopen(url=url, timeout=5).read()
    except (error.HTTPError, error.URLError):
        return None
    json_data = json.loads(resp.decode("utf-8"))
    return json_data.get('origin')


def update_record():
    url = 'https://dnsapi.cn/Record.Ddns'
    params = parse.urlencode({
        'login_token': os.getenv('LOGIN_TOKEN'),
        'format': 'json',
        'domain': os.getenv('DOMAIN'),
        'sub_domain': os.getenv('SUB_DOMAIN'),
        'record_id': os.getenv('RECORD_ID'),
        'record_line': '默认'
    })
    req = request.Request(url=url, data=params.encode('utf-8'), method='POST', headers=header())
    resp = request.urlopen(req).read().decode()
    records = json.loads(resp)
    print(records)


async def main():
    while 1:
        current_ip = get_ip()
        if current_ip and current_ip != os.getenv('CURRENT_IP'):
            os.environ['CURRENT_IP'] = current_ip
            update_record()
        try:
            interval = int(os.getenv('INTERVAL', 5))
        except ValueError:
            interval = 5
        await asyncio.sleep(interval)


def ask_exit(_sig_name):
    print("got signal %s: exit" % _sig_name)
    loop.stop()


if __name__ == '__main__':
    print('start...')
    read_config_to_env()
    check_config()
    loop = asyncio.get_event_loop()
    for sig_name in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig_name),
                                functools.partial(ask_exit, sig_name))
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, RuntimeError):
        print('stop...')
    finally:
        loop.close()
