
# dnspod-ddns

定时检查 ip 变化并更新dnspod的解析记录.

程序运行在python 3.5以上.

## 开始使用

### 本地运行

在 Linux 下，配置文件路径： `/etc/dnspod/ddnsrc` (也可通过环境变量设置)

在 Windows 下，配置文件路径为本目录下的：`ddnspod.cfg`

可配置的有效参数如下:

```config
LOGIN_TOKEN=token_id,token
DOMAIN=domain.com
SUB_DOMAIN=www
INTERVAL=5
EMAIL=you@email.com
IP_COUNT=1
```

* LOGIN_TOKEN : 必填, 在dnspod上申请的api组成的token,参考：https://support.dnspod.cn/Kb/showarticle/tsid/227/
* DOMAIN : 必填, 在dnspod解析的域名
* SUB_DOMAIN : 必填, 使用ddns的子域名
* INTERVAL: 选填, 轮询检查的时间间隔, 单位秒， 默认为5, 建议不要小于5
* EMAIL: 选填, 你的邮箱
* IP_COUNT: 选填, 你服务器的出口IP数量，一般为1，填大了一般也没事（玩 OpenWrt 的可能会有多个IP）

运行 `python ddns.py`

### Docker

和本地运行类似,需要配置参数.

参数的具体含义请参考**[本地运行](https://github.com/strahe/dnspod-ddns#%E6%9C%AC%E5%9C%B0%E8%BF%90%E8%A1%8C)**.

通过挂载配置文件方式:

```bash
docker run -d \
    --restart=always \
    --name=dnspod-ddns \
    -v your_ddnsrc_file_path:/etc/dnspod/ddnsrc \
     strahe/dnspod-ddns
 ```

通过传递环境变量的方式:

```bash
docker run -d \
    --restart=always \
    --name=dnspod-ddns \
    -e "login_token=token_id,token" \
    -e "domain=domain.com" \
    -e "sub_domain=www" \
    -e "interval=10" \
    -e "email=your@email.com" \
    -e "ip_count=1" \
    strahe/dnspod-ddns
```

### 测试环境

以下为测试通过的环境：
- [x] Windows 10
- [x] Windows Server 2016
- [x] Debian 4.9.8

尚未测试，应该能适配的环境：
- [ ] Centos
- [ ] Ubuntu
