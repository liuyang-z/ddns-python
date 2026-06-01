#!/usr/bin/env python

import time
import sys
import os
import json
import urllib.request
import urllib.parse
import requests
import re
import configparser

def _find_config():
    """查找 config.ini，优先级：环境变量 > ../config/ > /app/config.ini > ./config.ini"""
    search_paths = [
        os.environ.get('DDNS_CONFIG', ''),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.ini'),
        '/app/config.ini',
        os.path.join(os.getcwd(), 'config.ini'),
    ]
    for p in search_paths:
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError(
        "config.ini not found. Searched paths:\n  " +
        "\n  ".join(filter(None, search_paths))
    )


class DDNS(object):

    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read(_find_config())

        self._domain    = conf.get('Basic', 'Domain')
        self._subdomain = conf.get('Basic', 'SubDomain')
        self._token     = conf.get('Basic', 'DnspodToken')
        self._format    = 'json'

    def getDomainID(self):

        payload = {
            'login_token': self._token,
            'format': self._format
        }
        url = 'https://dnsapi.cn/Domain.List'

        response = self.POST(url, payload)

        if int(response['status']['code']) != 1:
            raise APIError("Code: 1 " + response['status']['message'])

        for domain in response['domains']:
            if domain['name'] == self._domain:
                return domain['id']

        raise APIError("Cant't fetch the info about the domain (%s)." % self._domain)

    def getRecordID(self, domainID):

        payload = {
            'login_token': self._token,
            'format': self._format,
            'domain_id': domainID
        }
        url = 'https://dnsapi.cn/Record.List'

        response = self.POST(url, payload)
        respRet = {}

        if int(response['status']['code']) != 1:
            raise APIError("Code: 2 " + response['status']['message'])

        for record in response['records']:

            if record['name'] == self._subdomain:
                respRet['id'] = record['id']
                respRet['value'] = record['value']
                respRet['recordLineID'] = record['line_id']
                return respRet

        raise APIError("Can't fetch the DNS record about the subdomain(%s)." % self._subdomain)

    def updateIP(self, domainID, recordID, recordLineID, hostIP):
        payload = {
            'login_token': self._token,
            'format': self._format,
            'domain_id': domainID,
            'record_id': recordID,
            'sub_domain': self._subdomain,
            'record_line_id': recordLineID,
            'value': hostIP
        }
        url = 'https://dnsapi.cn/Record.Ddns'

        response = self.POST(url, payload)

        if int(response['status']['code']) != 1:
            raise APIError("Code: 3 " + response['status']['message'])

        return 1

    def checkIP(self, recordIP, hostIP):

        if hostIP == recordIP:
            return 0
        else:
            return 1

    def getIP(self):

        html_text = requests.get("http://myip.ipip.net").text

        # print(html_text)

        trueIp =re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",html_text)

        data = trueIp.group(0)

        return data

    def POST(self, url, payload):

        try:
            data=bytes(urllib.parse.urlencode(payload), encoding='utf8')
            request_data = urllib.request.urlopen(url, data=data)
        except Exception as err:
            raise PostError("Code 5 %s" % err)
        else:
            return json.loads(request_data.read())

class Log(object):
    def __init__(self):
        # 日志目录：Docker 中用 /app/logs，本地开发用项目根目录下的 logs/
        if os.path.isdir('/app/logs'):
            self.rootPath = '/app'
        else:
            self.rootPath = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '..'
            )

    def info(self, msg):
        self.checkDir()
        filePath = self.rootPath + '/logs/info.log'
        self.writeMsg(filePath, msg)

    def error(self, msg):
        self.checkDir()
        filePath = self.rootPath + '/logs/error.log'
        self.writeMsg(filePath, msg)

    def checkDir(self):

        if not os.path.exists(self.rootPath + '/logs'):
            os.mkdir(self.rootPath + '/logs')

        return 1

    def writeMsg(self, Specfile, msg):
        try:
            fo = open(Specfile, 'a')
            fo.write(msg + '\n')
            fo.close()
        except Exception:
            pass

class Error(Exception):
    """Base class for exception in this module."""
    pass

class APIError(Error):
    """API Error, which is based on the official info."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class PostError(Error):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

if __name__ == '__main__':
    try:
        logs = Log()
        dynamic = DDNS()

        localTime = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        domainid = dynamic.getDomainID()
        record = dynamic.getRecordID(domainid)
        hostIP = dynamic.getIP()

        if int(dynamic.checkIP(record['value'], hostIP)) != 1:
            logs.info("[%s] No need to update record IP." % (localTime))
            sys.exit(0)

        dynamic.updateIP(domainid, record['id'], record['recordLineID'], hostIP)

        logs.info("[%s] The recored IP have updated to be : %s" % (localTime, hostIP))

    except PostError as err:
        logs.error("[%s] ERROR: %s" % (localTime, err))

    except APIError as err:
        logs.error("[%s] ERROR: %s" % (localTime, err))

    except Exception as err:
        logs.error("[%s] ERROR: %s" % (localTime, err))
