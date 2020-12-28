Socks5 Tune
===========

[![Build Status](https://drone.b7w.me/api/badges/b7w/socks5-tune/status.svg)](https://drone.b7w.me/b7w/socks5-tune)

A simple supervisor for ssh sock5 tunnel, plus web server for Proxy Auto-Configuration (PAC) profiles.


Configuration
-------------

Example of `docker-compose.yml`:

```yaml
version: "3"
services:
    app:
        image: 'registry.b7w.me/b7w/socks5-tune:latest'
        restart: always
        ports:
            - 1080:1080
            - 8070:8000
        environment:
            - APP_PRIVATE_KEY=/storage/private-key.pem
            - APP_DESTINATION=socks5-tune@vpc2.b7w.me
            - APP_STORAGE_PATH=/storage
        volumes:
            - ./storage:/storage
        logging:
            driver: json-file
            options:
                max-file: "4"
                max-size: "1m"
```

Requests:

```http request
### Status
GET http://127.0.0.1:8000/status


### Create/Update profile
POST http://127.0.0.1:8000/profile/test.pac

function FindProxyForURL(url, host) {
    if (shExpMatch(host, "ifconfig.me")) {
        return "SOCKS 127.0.0.1:1080";
    }
    return "DIRECT";
}


### Profile url for Browser setup
GET http://127.0.0.1:8000/profile/test.pac



### Delete profile
DELETE http://127.0.0.1:8000/profile/test.pac
```

About
-----

socks5-tune is open source project, released by MIT license.

Look, feel, be happy :-)
