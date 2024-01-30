# python 2.6
import csv
import json
import urllib2
import time
import urllib


def send_notification(message, tg_chat_id, tg_token):
    url = 'https://api.telegram.org/bot{0}/sendMessage'.format(tg_token)
    values = {'chat_id': tg_chat_id, 'text': message}

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    urllib2.urlopen(req)


def convert_hlr2_to_hlr3(hlr2_file, hlr3_file):
    with open(hlr2_file, 'r') as hlr2_file:
        next(hlr2_file)
        csv_reader = csv.DictReader(
            hlr2_file,
            delimiter=';',
            fieldnames=('DIAL_CODE', 'MCC_MNC'),
            quotechar='"',
        )
        with open(hlr3_file, 'w') as hlr3_file:
            csv_writer = csv.DictWriter(
                hlr3_file,
                delimiter=';',
                fieldnames=('dnis', 'mccmnc', 'active_from', 'ownerID', 'providerResponseCode'),
            )
            for row in csv_reader:
                csv_writer.writerow({
                    'dnis': row['DIAL_CODE'],
                    'mccmnc': row['MCC_MNC'],
                    'active_from': int(time.time()),
                    'ownerID': None,
                    'providerResponseCode': None,
                })


def load_hlr3_data(file_path, replace_all=False):
    url = 'http://127.0.0.1:42082/http/api/?login=hlr_configurator&password=hlr_configurator'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'method': 'Mnp.Update',
        'params': {
            'filePath': file_path,
            'replaceAll': replace_all,
            'skipFirstLine': False,
            'force': True,
            'diffRequest': False,
        },
        'id': 999,
        'jsonrpc': '2.0',
    }
    json_data = json.dumps(data)
    req = urllib2.Request(url, json_data, headers)

    response = urllib2.urlopen(req)
    return response.read()


def join_files(final_file, *args):
    with open(final_file, 'w') as f:
        for file in args:
            with open(file, 'r') as f_in:
                f.write(f_in.read())


def main():
    tg_token = ''
    tg_chat_id = ''
    hlr3_for_load = '/tmp/hlr3_for_load.csv'
    hlr3_file = '/tmp/hlr3_full.csv'
    hlr3_dial_code = '/tmp/refbook_for_hlr_3.csv'
    dial_code_file = '/u01/app/oracle/invoice.files/refbook_for_hlr_2.csv'

    convert_hlr2_to_hlr3(dial_code_file, hlr3_dial_code)
    join_files(hlr3_for_load,  hlr3_file, hlr3_dial_code)
    load_result = load_hlr3_data(hlr3_for_load, True)
    load_result = json.loads(load_result)
    message = 'mnp load result: handledLines - {0}, successfullyLines - {1}'.format(
        load_result['result']['handledLines'],
        load_result['result']['successfullyLines'],
    )
    send_notification(message=message, tg_token=tg_token, tg_chat_id=tg_chat_id)


if __name__ == '__main__':
    main()
