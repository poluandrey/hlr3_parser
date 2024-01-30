import csv
import zipfile
import ftplib
import os
import paramiko

from scp import SCPClient
from datetime import datetime
from pathlib import Path

from config import settings
from logger_config import configure_logger
from parsers.parser import AvailableCountry, ParseResult

logger = configure_logger(__name__)


def get_latest_file_from_ftp(ftp: ftplib.FTP) -> str:
    logger.debug('Fetching latest file from FTP')
    entries = list(filter(lambda entrie: entrie[1]['type'] == 'file', list(ftp.mlsd())))
    entries.sort(key=lambda entry: entry[1]['modify'], reverse=True)
    file = entries[0][0]
    logger.debug(f'Latest file: {file}')
    return file


def download_file(
        file_name: str,
        ftp: ftplib.FTP,
) -> Path:
    # download file from FTP and return path to file
    logger.debug(f'Downloading {file_name}')
    download_path = Path(settings.tmp_directory).joinpath(file_name)
    with open(download_path, 'wb') as f:
        ftp.retrbinary(f'RETR {file_name}', f.write)

    logger.debug(f'Finished downloading {file_name}')
    return download_path


def archive_file(
        source_file: str,
        file_prefix: str,
) -> None:
    logger.debug(f'Starting archiving {source_file}')
    archive_name = f'{file_prefix}-{datetime.now().strftime("%Y%m%d")}.zip'
    archive_file = os.path.join(settings.archive_dir, archive_name)
    logger.debug(f'Archive file: {archive_file}')
    with zipfile.ZipFile(archive_file, 'w') as zip_file:
        zip_file.write(source_file, arcname=os.path.basename(source_file))

    logger.debug('Finished archiving')


def get_country_prefix(country: AvailableCountry) -> str:
    match country:
        case country.Belarus:
            return settings.belarus_settings.file_prefix
        case country.Kazakhstan:
            return settings.kazakhstan_settings.file_prefix
        case country.Latvia:
            return settings.latvia_settings.file_prefix


def push_file_to_server(server: str, port: int, source_file: str, destination_path: str) -> None:
    logger.info(f'Pushing {source_file} to {server}:{destination_path}')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        server,
        port,
        username=settings.smssw_user,
        disabled_algorithms={
            'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256'],
        },
    )

    scp = SCPClient(ssh.get_transport())
    scp.put(source_file, destination_path)
    scp.close()
    ssh.close()


def save_parse_result(parsed_result: ParseResult, country: AvailableCountry) -> None:
    logger.info('start save parse result')

    hlr3_fields = ('dnis', 'mccmnc', 'active_from', 'ownerID', 'providerResponseCode')
    ftp_fields = ('dnis', 'mccmnc')
    file_prefix = get_country_prefix(country)

    ftp_file = os.path.join(settings.ftp_directory, file_prefix, f'{file_prefix}.csv')
    logger.info(f'saving ftp file to: {ftp_file}')

    with open(ftp_file, 'w') as ftp_f:
        csv_writer = csv.DictWriter(ftp_f, fieldnames=ftp_fields, delimiter=';')
        csv_writer.writerows(parsed_result.hlr_records)

    hlr3_file = os.path.join(settings.hlr_directory, file_prefix, f'{file_prefix}.csv')
    logger.info(f'saving hlr3 file to: {hlr3_file}')

    with open(hlr3_file, 'w') as hlr_f:
        csv_writer = csv.DictWriter(hlr_f, fieldnames=hlr3_fields, delimiter=';')
        csv_writer.writerows(parsed_result.hlr3_records)

    logger.info('finishing save parse result')
