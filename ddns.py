import asyncio
import os
import json
import signal
import functools
import logging
import socket
from urllib import request, error, parse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def read_config_to_env():    
    # linux
    config_path = '/etc/dnspod/ddnsrc'

    # windows
    if os.name == 'nt':
        config_path = 'ddnspod.cfg'
    
    if os.path.isfile(config_path):
        try:
            f = open(config_path)
            for item in f:
                if '\n' == item:
                    continue
                item = item.split('=')
                
                os.environ[item[0]] = item[1].split()[0]
            f.close()
        except IndexError:
            logging.error('config error')
            exit()
    if not os.getenv('RECORD_ID'):
        logging.info("DDNS: %s.%s" % (os.getenv('SUB_DOMAIN'), os.getenv('DOMAIN')))
        record_id = get_record_id(os.getenv('DOMAIN'), os.getenv('SUB_DOMAIN'))
        assert None != record_id, "未找到记录id，请检查DNSPOD设置里有没有设置 %s.%s 的 A 记录" % (os.getenv('SUB_DOMAIN'), os.getenv('DOMAIN'))
        os.environ['RECORD_ID'] = record_id
    logging.info('config loaded')


def check_config():
    login_token = os.getenv('LOGIN_TOKEN')
    domain = os.getenv('DOMAIN')
    sub_domain = os.getenv('SUB_DOMAIN')
    if not (login_token and domain and sub_domain):
        logging.error('config error')
        exit()
    logging.info('config checked')

# 这个函数在本地 DNS 遭受污染时失效
def get_ip():
    url = 'http://www.httpbin.org/ip'
    try:
        resp = request.urlopen(url=url, timeout=10).read()
    except (error.HTTPError, error.URLError, socket.timeout):
        return None
    json_data = json.loads(resp.decode("utf-8"))
    return json_data.get('origin')

# 这个函数可以在本地 DNS 遭受污染的时候获取到IP
# 如需模拟DNS污染，可以在HOSTS文件里加入 127.0.0.1 www.httpbin.org
def get_ip_2():
    url = 'http://52.5.182.176/ip'
    try:
        req = request.Request(url=url, method='GET', headers={'Host': 'www.httpbin.org'})
        resp = request.urlopen(req).read()
    except (error.HTTPError, error.URLError, socket.timeout):
        return None
    json_data = json.loads(resp.decode("utf-8"))
    return json_data.get('origin')


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
    try:
        resp = request.urlopen(req).read().decode()
    except (error.HTTPError, error.URLError, socket.timeout):
        return None
    records = json.loads(resp).get('records', {})
    for item in records:
        if item.get('name') == sub_domain:
            return item.get('id')
    return None


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
    logging.info(records)


async def main():
    while 1:
        current_ip = get_ip() or get_ip_2()
        
        if current_ip == None:
            logging.error('get current ip FAILED.')

        if current_ip and current_ip != os.getenv('CURRENT_IP'):
            # TODO：
            # 对于拥有多个出口 IP 的服务器，上面的 get_ip() 函数会在几个 ip 之间不停切换
            # 然后频繁进入这个判断，进行 update_record()，然后很快就会触发 API Limited 了
            # 也许可以找点办法查询一下所有各 ip 是否可用……
            #
            # 测试用的代码：
            # logging.info('ip发生了更改(%s->%s)' %(os.getenv('CURRENT_IP'), current_ip))
            # 
            os.environ['CURRENT_IP'] = current_ip
            update_record()
        try:
            interval = int(os.getenv('INTERVAL', 5))
        except ValueError:
            interval = 5
        await asyncio.sleep(interval)


def ask_exit(_sig_name):
    logging.warning('got signal {}: exit'.format(_sig_name))
    loop.stop()


if __name__ == '__main__':
    logging.info('start...')
    read_config_to_env()
    check_config()
    loop = asyncio.get_event_loop()
    for sig_name in ('SIGINT', 'SIGTERM'):
        try:
            loop.add_signal_handler(getattr(signal, sig_name), functools.partial(ask_exit, sig_name))
        except NotImplementedError:
            pass  # Ignore if not implemented. Means this program is running in windows.
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, RuntimeError):
        logging.info('stop...')
    finally:
        loop.close()
