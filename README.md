# scrape-web

## How to use this?
`scrape_class.py` provides a class `UserAgent` which can cycle through different headers, proxies, IP addresses etc. to help scrape your website.

You have an option use TOR (by setting the field `USE_TOR` to True) to cycle through different IP addresses. You will however have to install TOR related packages to get this going. Instruction on this below.

An example implementation of `UserAgent` is shown in `scrape_site.py`.

## An excellent resource to setup TOR on your machine and access via Python
https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b

Pasting the content here as a mirror.

## A step-by-step guide how to use Python with Tor and Privoxy

Tested on Ubuntu 16.04 Docker container. The Dockerfile is a single line `FROM ubuntu:16.04`.

NOTE: stopping services didn't work for me for some reason. That's why there is `pidof <service name> | xargs kill` after each failed `service <service name> stop` to kill it.

## References
* [How to request new TOR identity in terminal](https://stackoverflow.com/q/16987518/4183498)
* [How to anonymize the programs from your terminal with torify](https://linuxaria.com/howto/how-to-anonymize-the-programs-from-your-terminal-with-torify)
* [How To: Using Tor From The Command Line](https://justhackerthings.com/post/using-tor-from-the-command-line/)
* [How to change Tor identity in Python?](https://stackoverflow.com/q/9887505/4183498)
* [Make requests using Python over Tor](https://stackoverflow.com/q/30286293/4183498)
* [Crawling anonymously with Tor in Python](http://sacharya.com/crawling-anonymously-with-tor-in-python/)
  * [Alternative link (Gist) for "Crawling anonymously with Tor in Python"](https://gist.github.com/KhepryQuixote/46cf4f3b999d7f658853)
* [Tor IP changing and web scraping](https://dm295.blogspot.com/2016/02/tor-ip-changing-and-web-scraping.html)


## Related
* [A step-by-step guide how to use Tor without Authentication](https://gist.github.com/DusanMadar/c1155329cf6a71e4346cae271a2eafd3)
* [TorIpChanger - Python powered way to get a unique Tor IP](https://github.com/DusanMadar/TorIpChanger)


## Steps

### 1. Install and check Tor status
```
root@75f6721089f2:/# apt update
root@75f6721089f2:/# apt install tor
root@75f6721089f2:/# service tor status
 * tor is not running
 ```

### 2. Start Tor and check it's running
```
root@75f6721089f2:/# service tor start 
 * Starting tor daemon...          [ OK ] 
root@75f6721089f2:/# service tor status
 * tor is running
```


### 3. Try to Authenticate with nc (Netcat)
It's not possible to connect as `ControlPort` is not set yet.
```
root@75f6721089f2:/# apt install netcat
root@75f6721089f2:/# echo -e 'AUTHENTICATE' | nc 127.0.0.1 9051
(UNKNOWN) [127.0.0.1] 9051 (?) : Connection refused
```


### 4. Stop/kill Tor, set ControlPort and start Tor again
```
root@75f6721089f2:/# service tor stop
 * Stopping tor daemon...          [fail]
root@75f6721089f2:/# pidof tor | xargs kill
root@75f6721089f2:/# service tor status
 * tor is not running
root@75f6721089f2:/# echo "ControlPort 9051" >> /etc/tor/torrc
root@75f6721089f2:/# service tor start 
 * Starting tor daemon...          [ OK ] 
```


### 5. Try to Authenticate with nc again
It's possible to connect but Authentication fails.
```
root@75f6721089f2:/# echo -e 'AUTHENTICATE' | nc 127.0.0.1 9051
515 Authentication failed: Wrong length on authentication cookie.
```


### 6. Stop/kill Tor, set and check `HashedControlPassword` then start Tor again

Make sure that you have something like `HashedControlPassword 16:ED2893D8EC97801C60DF4A72249CBCCD8B97B3B01A15C923DC49A0E500` (actual password hash can/will differ) in `/etc/tor/torrc`.

```
root@75f6721089f2:/# service tor stop
 * Stopping tor daemon...          [fail]
root@75f6721089f2:/# pidof tor | xargs kill
root@75f6721089f2:/# echo HashedControlPassword $(tor --hash-password "my password" | tail -n 1) >> /etc/tor/torrc
root@75f6721089f2:/# tail -n 2 /etc/tor/torrc
ControlPort 9051
HashedControlPassword 16:ED2893D8EC97801C60DF4A72249CBCCD8B97B3B01A15C923DC49A0E500
root@75f6721089f2:/# service tor start 
 * Starting tor daemon...          [ OK ] 
```


### 7. Try to Authenticate with nc again
Authentication passes with a correct password.
```
# NOTE Use Ctrl+C to exit.
root@75f6721089f2:/# echo -e 'AUTHENTICATE' | nc 127.0.0.1 9051
515 Authentication failed: Password did not match HashedControlPassword *or* authentication cookie.
root@75f6721089f2:/# echo -e 'AUTHENTICATE "my password"' | nc 127.0.0.1 9051
250 OK
```


### 8. Check your public IP and currently used Tor ip
```
root@75f6721089f2:/# apt install curl
root@75f6721089f2:/# curl http://icanhazip.com/ 
89.196.159.79
root@75f6721089f2:/# torify curl http://icanhazip.com/   
185.220.101.17
```


### 9. Change and check Tor IP
```
root@75f6721089f2:/# echo -e 'AUTHENTICATE "my password"\r\nsignal NEWNYM\r\nQUIT' | nc 127.0.0.1 9051
250 OK
250 OK
250 closing connection
root@75f6721089f2:/# torify curl http://icanhazip.com/
185.220.101.6
```


### 10. Change (with Python3) and check Tor IP
```
root@75f6721089f2:/# apt install python3
root@75f6721089f2:/# apt install python3-pip
root@75f6721089f2:/# pip3 install stem
root@75f6721089f2:/# python3
Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from stem import Signal
>>> from stem.control import Controller
>>> 
>>> with Controller.from_port(port=9051) as controller:
...     controller.authenticate()
...     controller.signal(Signal.NEWNYM)
... 
>>> 
root@75f6721089f2:/# torify curl http://icanhazip.com/
185.107.81.233
```


### 11. Install privoxy and check traffic is routed through Tor

Now that it's clear Tor is configured and works properly we can include `privoxy` to the loop.

```
root@75f6721089f2:/# apt install privoxy
root@75f6721089f2:/# service privoxy status
 * privoxy is not running
root@75f6721089f2:/# echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config
root@75f6721089f2:/# service privoxy start
 * Starting filtering proxy server privoxy          [ OK ]
root@75f6721089f2:/# torify curl http://icanhazip.com/
176.10.99.200
root@75f6721089f2:/# curl -x 127.0.0.1:8118 http://icanhazip.com/
176.10.99.200
```


### 12. Change and check Tor IP solely with Python3
```
root@75f6721089f2:/# pip3 install requests
root@75f6721089f2:/# python3
Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>>
>>> from stem import Signal
>>> from stem.control import Controller
>>>
>>> response = requests.get('http://icanhazip.com/', proxies={'http': '127.0.0.1:8118'})
>>> response.text.strip()
'137.74.171.94'
>>> 
>>> with Controller.from_port(port=9051) as controller:
...     controller.authenticate(password='my password')
...     controller.signal(Signal.NEWNYM)
... 
>>> response = requests.get('http://icanhazip.com/', proxies={'http': '127.0.0.1:8118'})
>>> response.text.strip()
'87.118.92.43'
>>> 
```


### 13. Change and check Tor IP with [TorIpChanger](https://github.com/DusanMadar/TorIpChanger)
```
root@75f6721089f2:/# pip3 install toripchanger
root@75f6721089f2:/# python3
Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from toripchanger import TorIpChanger
>>> 
>>> tor_ip_changer = TorIpChanger(tor_password='my password', tor_port=9051, local_http_proxy='127.0.0.1:8118')
>>> tor_ip_changer.get_new_ip()
'185.24.218.182'
>>> 
```
