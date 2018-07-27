import asyncio
import os
import json
import signal
import functools
import logging
import socket
from urllib import request, error, parse
from config import read_config, save_config, check_config, cfg
from get_ip import get_ip

def header():
    h = {
        'User-Agent': 'Client/0.0.1 ({})'.format(cfg['email'])
    }
    return h

def get_record_id(domain, sub_domain):
    url = 'https://dnsapi.cn/Record.List'
    params = parse.urlencode({
        'login_token': cfg['login_token'],
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
    try:
        url = 'https://dnsapi.cn/Record.Ddns'
        params = parse.urlencode({
            'login_token': cfg['login_token'],
            'format': 'json',
            'domain': cfg['domain'],
            'sub_domain': cfg['sub_domain'],
            'record_id': cfg['record_id'],
            'record_line': '默认'
        })
        req = request.Request(url=url, data=params.encode('utf-8'), method='POST', headers=header())
        resp = request.urlopen(req).read().decode()
        records = json.loads(resp)
        logging.info("record updated: %s" % records)
    except:
        

async def main():
    while 1:
        current_ip = get_ip()
        if not current_ip:
            logging.error('get current ip FAILED.')
            continue
        
        # 对于拥有多个出口 IP 负载均衡的服务器，上面的 get_ip() 函数会在几个 ip 之间不停切换
        # 然后频繁进入这个判断，进行 update_record()，然后很快就会触发 API Limited 了
        
        # ip_count = int(cfg['ip_count'])
        # ip_pool = cfg['ip_pool'].split(',')[:ip_count]
        # if current_ip in ip_pool:
            
        # cfg['ip_pool'] = ','.join([str(x) for x in pool)
        if current_ip != cfg['current_ip']:
            update_record()

        try:
            interval = int(cfg['interval'])
        except ValueError:
            interval = 5
        await asyncio.sleep(interval)


def ask_exit(_sig_name):
    logging.warning('got signal {}: exit'.format(_sig_name))
    loop.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    logging.info('start...')
    read_config()
    check_config()
    loop = asyncio.get_event_loop()
    for sig_name in ('SIGINT', 'SIGTERM'):
        try:
            loop.add_signal_handler(getattr(signal, sig_name), functools.partial(ask_exit, sig_name))
        except NotImplementedError:
            pass  # 使兼容 WINDOWS
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, RuntimeError):
        logging.info('stop...')
    finally:
        loop.close()