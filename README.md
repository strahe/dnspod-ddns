## dnspod-ddns

定时检查ip变化并更新dnspod的解析记录.

程序运行在python 3.5以上.

## 开始使用

### 本地运行

配置文件路径： `/etc/dnspod/ddnsrc` (也可通过环境变量设置)

在 Windows 下，配置文件路径为本目录下的：`ddnspod.cfg`

可配置的有效参数如下:
```
LOGIN_TOKEN=token_id,token
DOMAIN=domain.com
SUB_DOMAIN=www
INTERVAL=5
EMAIL=you@email.com
```

* LOGIN_TOKEN : 必填, 在dnspod上申请的API组成的token,参考：https://support.dnspod.cn/Kb/showarticle/tsid/227/
* DOMAIN : 必填, 在dnspod解析的域名
* SUB_DOMAIN : 必填, 使用ddns的子域名
* INTERVAL: 选填, 轮询检查的时间间隔, 单位秒， 默认为5, 建议不要小于5
* EMAIL: 选填, 你的邮箱

运行`python ddns.py`

### Docker

和本地运行类似,需要配置参数.

参数的具体含义请参考**本地运行**.

通过挂载配置文件方式:

```
docker run -d \
    --restart=always \
    --name=dnspod-ddns \
    -v your_ddnsrc_file_path:/etc/dnspod/ddnsrc\
     strahe/dnspod-ddns
 ```

通过传递环境变量的方式:

```
docker run -d \
    --restart=always \
    --name=dnspod-ddns \
    -e "LOGIN_TOKEN=token_id,token" \
    -e "DOMAIN=domain.com" \
    -e "SUB_DOMAIN=www"\
    -e "INTERVAL=10" \
    -e "EMAIL=your@email.com" \
    strahe/dnspod-ddns
```
