Socks5 Tune
===========

[![Build Status](https://drone.b7w.me/api/badges/b7w/socks5-tune/status.svg)](https://drone.b7w.me/b7w/socks5-tune)

A simple supervisor for ssh sock5 tunnel, plus web server for Proxy Auto-Configuration (PAC) profiles.


Configuration
-------------

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
            - APP_STORAGE=/storage
        volumes:
            - ./storage:/storage
        logging:
            driver: json-file
            options:
                max-file: "4"
                max-size: "1m"
```

About
-----

Socks5-tune is open source project, released by MIT license.

Look, feel, be happy :-)
