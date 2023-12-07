#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8:ts=8:et:sw=4:sts=4
#
# Copyright © 2023 Johannes Bosecker <j.bosecker.dev@icloud.com>
#
# Distributed under terms of the MIT license.

"""

"""

from struct import (pack, unpack, calcsize)
from enum import Enum
import socket
import logging

LOGGER = logging.getLogger("iluminize")

_ILUMINIZE_SENDER_LEN = 3
_ILUMINIZE_PKT_LEN = 12


class IluminizeController(object):

    def __init__(self, host, port, sender):
        self.host = host
        self.port = port
        self.sender = sender

    def set_rgb(self, red, green, blue):
        (d1, d2, d3) = self._get_device_id()
        packet = pack("BBBBBBBBBBBB", 0x55, d1, d2, d3, 0xf2, 0x01, int(red), int(green), int(blue), 0x00, 0xaa, 0xaa)
        self._send(packet)

    def set_white(self, white):
        (d1, d2, d3) = self._get_device_id()
        packet = pack("BBBBBBBBBBBB", 0x55, d1, d2, d3, 0x00, 0x01, 0x08, 0x4b, int(white), 0x00, 0xaa, 0xaa)
        self._send(packet)

    def _send(self, packet, sock=None):
        if len(packet) != _ILUMINIZE_PKT_LEN:
            raise Exception('Invalid data length. Packet malformed')
            
        packet = self._replace_checksum(packet)
        # double the command, so the chance of successful transmission is increased
        payload = packet + packet
        
        LOGGER.debug("Sending bytes: %s", payload.hex())
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self._get_remote_socket())
            sock.sendall(payload)
            sock.close()
        except OSError as oserr:
            if oserr.errno == 101:
                LOGGER.error("Network is unreachable")
            else:
                LOGGER.error("OSError happend while sending (%i)", oserr.errno)
        except:
            LOGGER.error("Error happend while sending")

    def _get_remote_socket(self):
        return (self.host, self.port)
        
    def _get_device_id(self):
        d1 = int(self.sender[0:2], 16)
        d2 = int(self.sender[2:4], 16)
        d3 = int(self.sender[4:6], 16)
                
        return (d1, d2, d3)
        
    def _replace_checksum(self, packet):
        values = bytearray(packet)
        
        checksum = 0
        length = len(values)
        
        for i in range(4, length - 3):
            checksum += values[i]
    
        checksum %= 0x100
        values[length - 3] = checksum
        return bytes(values)
