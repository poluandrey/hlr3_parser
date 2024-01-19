# python 2.6
import os
import urllib
from dotenv import load_dotenv


load_dotenv()

DEBUG = os.getenv('DEBUG')


def load_hlr3_data(file, replace_all=False, ):
    url = 'http://127.0.0.1:42082/http/api/?login=hlr_configurator&password=hlr_configurator'
    data = {
        "method": "Mnp.Update",
        "params": {
            "filePath": "/tmp/hlr3_full.csv",
            "replaceAll": replace_all,
            "skipFirstLine": False,
            "force": True,
            "diffRequest": False
        },
        "id": 123,
        "jsonrpc": "2.0"
    }

    resp = urllib.urlopen(url, data=data)

    print(resp.read())
    os.remove(file)
