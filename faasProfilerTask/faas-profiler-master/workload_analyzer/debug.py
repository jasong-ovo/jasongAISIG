import json
import os
from wskutil import request
import sys
def GetActivationRecordsSince(since, limit=100):
    """
    Returns details on activation records since a given tick in milliseconds
    """
    # configs = GetDBConfigs()
    # url = configs['db_protocol']+'://'+configs['db_host']+':' + \
    #     configs['db_port']+'/'+'whisk_local_activations/_find'
    url = 'http' + '://' + '10.244.1.221' + ':' + \
    '5984' + '/' + 'test_activations/_find'
    headers = {
        'Content-Type': 'application/json',
    }
    body = {
        "selector": {
            "start": {
                "$gte": since
            }
        },
        "limit": limit
    }

    # res = request('POST', url, body=json.dumps(body), headers=headers,
    #               auth='%s:%s' % (configs['db_username'], configs['db_password']))

    res = request('POST', url, body=json.dumps(body), headers=headers,
                auth='%s:%s' % ('whisk_admin', 'some_passw0rd'))

    # return res.read()
    return json.loads(res.read())


if __name__ == '__main__':
     info = GetActivationRecordsSince(1619764693886, limit=100)
     print(info)
