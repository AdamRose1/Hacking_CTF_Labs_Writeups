#!/usr/bin/env python

"""
Created this script to solve the HackTheBox Academy lab called 'Error-Based SQL Injection' for the module called 'Advanced SQL Injections'
I created this tamper script because sqlmap will not find the sql injection without it since the regex filter requires the input email to end with @anything.com. 
By using this tamper script, sqlmap will find the sql injection.  Place this python tamper script in /usr/share/sqlmap/tamper/ and then run sqlmap with --tamper=name-of-this-file
"""

import os

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOWEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    return payload + '@test.com'  # adds @test.com to the end of each payload
