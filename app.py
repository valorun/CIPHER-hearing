#!/usr/bin/python3
# coding: utf-8

import logging
from cipher_hearing import create_app, setup_logger
from cipher_hearing.config import client_config

DEBUG = client_config.DEBUG

if __name__ == '__main__':
    setup_logger(debug=DEBUG)
    client = create_app(debug=DEBUG)
    logging.info("Application started")
    client.loop_forever()