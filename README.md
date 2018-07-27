## dnspod-ddns

定时检查 ip 变化并更新dnspod的解析记录.

程序运行在python 3.5以上.

以下为测试通过的环境：
- Windows 10
- Windows Server 2016

## 开始使用

### 本地运行

在 Linux 下，配置文件路径： `/etc/dnspod/ddnsrc` (也可通过环境变量设置)

在 Windows 下，配置文件路径为本目录下的：`ddnspod.cfg`

可配置的有效参数如下:
```
login_token=token_id,token
domain=domain.com
sub_domain=www
interval=5
email=you@email.com
ip_count=1
```

* login_token : 必填, 在dnspod上申请的api组成的token,参考：https://support.dnspod.cn/kb/showarticle/tsid/227/
* domain : 必填, 在dnspod解析的域名
* sub_domain : 必填, 使用ddns的子域名
* interval: 选填, 轮询检查的时间间隔, 单位秒， 默认为5, 建议不要小于5
* email: 选填, 你的邮箱
* ip_count: 选填, 你服务器的出口IP数量，一般为1，填大了一般也没事（玩 OpenWrt 的可能会有多个IP）

运行 `python ddns.py`

### Docker

和本地运行类似,需要配置参数.

参数的具体含义请参考**本地运行**.

通过挂载配置文件方式:

```
docker run -d                                   \
    --restart=always                            \
    --name=dnspod-ddns                          \
    -v your_ddnsrc_file_path:/etc/dnspod/ddnsrc \
     strahe/dnspod-ddns
 ```

通过传递环境变量的方式:

```
docker run -d                       \
    --restart=always                \
    --name=dnspod-ddns              \
    -e "login_token=token_id,token" \
    -e "domain=domain.com"          \
    -e "sub_domain=www"             \
    -e "interval=10"                \
    -e "email=your@email.com"       \
    -e "ip_count=1"                 \
    strahe/dnspod-ddns
```
