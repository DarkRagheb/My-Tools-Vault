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
import urllib.request, urllib.parse, urllib.error

class EncoderDecoder(object):
    """
    Class to help encoding and decoding strings with different hashing or
    encoding algorigthms..
    """
    # encdec functions:
    def __init__(self):
        self.encmap = { "Str" : lambda x : self._fromCharCodeEncode(x),
                   "Hex" : lambda x : self._hexEncode(x),
                   "Hes" : lambda x : self._hexSemiEncode(x),
                   "Une" : lambda x : self._unEscape(x),
                   "Dec" : lambda x : self._decEncode(x),
                   "Mix" : lambda x : self._unEscape(self._fromCharCodeEncode(x)),
                   "Dou" : lambda x : self._doubleUrlEncode(x),
                   "Ent" : lambda x : self._htmlEntityEncode(x),
                   "Cas" : lambda x : self._mixedCaseEncode(x),
                   "Uni" : lambda x : self._jsUnicodeEncode(x),
                   "Xhx" : lambda x : self._jsHexEncode(x),
                   "Ocb" : lambda x : self._jsOctalEncode(x)
                   }

    def _fromCharCodeEncode(self, string):
        """
        Encode to string.
        """
        encoded=''
        for char in string:
            encoded=encoded+","+str(ord(char))
        return encoded[1:]

    def _hexEncode(self, string):
        """
        Encode to hex.
        """
        encoded=''
        for char in string:
            encoded=encoded+"%"+hex(ord(char))[2:]
        return encoded

    def _hexSemiEncode(self, string):
        """
        Encode to semi hex.
        """
        encoded=''
        for char in string:
            encoded=encoded+"&#x"+hex(ord(char))[2:]+";"
        return encoded

    def _decEncode(self, string):
        """
        Encode to decimal.
        """
        encoded=''
        for char in string:
            encoded=encoded+"&#"+str(ord(char))
        return encoded

    def _unEscape(self, string):
        """
        Escape string.
        """
        encoded=''
        for char in string:
            encoded=encoded+urllib.parse.quote(char)
        return encoded

    def _doubleUrlEncode(self, string):
        """
        Encode with double URL encoding.
        """
        return urllib.parse.quote(urllib.parse.quote(string))

    def _htmlEntityEncode(self, string):
        """
        Encode to HTML named entities.
        """
        entities = {'<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;','(':'&lpar;',')':'&rpar;',':':'&colon;','=':'&equals;','/':'&sol;','`':'&grave;',';':'&semi;','&':'&amp;'}
        encoded=''
        for char in string:
            encoded=encoded+entities.get(char, char)
        return encoded

    def _mixedCaseEncode(self, string):
        """
        Mutate to mixed case.
        """
        encoded=''
        i=0
        for char in string:
            if char.isalpha():
                encoded=encoded+(char.upper() if i%2==0 else char.lower())
                i=i+1
            else:
                encoded=encoded+char
        return encoded

    def _jsUnicodeEncode(self, string):
        """
        Encode to JS unicode escape.
        """
        encoded=''
        for char in string:
            encoded=encoded+"\\u%04x" % ord(char)
        return encoded

    def _jsHexEncode(self, string):
        """
        Encode to JS hexadecimal escape.
        """
        encoded=''
        for char in string:
            encoded=encoded+"\\x%02x" % ord(char)
        return encoded

    def _jsOctalEncode(self, string):
        """
        Encode to JS octal escape.
        """
        encoded=''
        for char in string:
            encoded=encoded+"\\"+oct(ord(char))[2:]
        return encoded

    def _ipDwordEncode(self, string):
        """
        Encode to dword.
        """
        encoded=''
        tblIP = string.split('.')
        # In the case it's not an IP
        if len(tblIP)!=4:
            return 0
        for number in tblIP:
            tmp=hex(int(number))[2:]
            if len(tmp)==1:
                tmp='0' +tmp 
            encoded=encoded+tmp
        return int(encoded,16)
	
    def _ipOctalEncode(self, string):
        """
        Encode to octal.
    	"""
        encoded=''
        tblIP = string.split('.')
        # In the case it's not an IP
        if len(tblIP)!=4:
            return 0
        octIP = [oct(int(s)).zfill(4) for s in tblIP]
        return ".".join(octIP)

if __name__ == "__main__":
    encdec = EncoderDecoder()
    print(encdec._ipOctalEncode("127.0.0.1"))
