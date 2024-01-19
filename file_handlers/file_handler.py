import csv
import ftplib
import os

from typing import Protocol
from zipfile import ZipFile

from config import georgia_settings, default_settings, kazakhstan_settings, belarus_settings
from error.errors import GetFileError
from logger_config import configure_logger
from parsers.parser import AvailableCountry, ParseResult
from utils import get_latest_file_from_ftp, download_file, get_country_prefix

logger = configure_logger(__name__)


class FileHandler(Protocol):

    def get_file(self) -> str:
        pass

    def save_parse_result(self, parsed_result: ParseResult) -> None:
        pass


class GeorgiaFileHandler:

    def get_file(self) -> str:
        """
        Get a file from FTP
        :return: path of the extracted file
        """
        ftp = ftplib.FTP()
        try:
            ftp.connect(georgia_settings.ftp_server, georgia_settings.ftp_port, timeout=20)
            ftp.login(georgia_settings.ftp_user, georgia_settings.ftp_password)
        except TimeoutError as err:
            logger.error(f'could not connect to {georgia_settings.ftp_server}:{georgia_settings.ftp_port}')
            raise GetFileError()
        latest_file = get_latest_file_from_ftp(ftp)
        zip_file = download_file(latest_file, ftp=ftp)
        ftp.quit()
        with ZipFile(zip_file, 'r') as zip_ref:
            raw_mnp_file = os.path.join(default_settings.tmp_directory, zip_ref.namelist()[0])
            zip_ref.extractall(georgia_settings.tmp_directory)
        logger.info(f'extracted {raw_mnp_file}')
        logger.info(f'remove zip file: {zip_file}')
        os.remove(zip_file)
        return raw_mnp_file

    def save_parse_result(self, parsed_result: ParseResult) -> None:
        hlr3_fields = ('dnis', 'mccmnc', 'active_from', 'ownerID', 'providerResponseCode')
        ftp_fields = ('dnis', 'mccmnc')
        ftp_file = os.path.join(default_settings.ftp_directory, georgia_settings.file_prefix,
                                f'{georgia_settings.file_prefix}.csv')

        with open(ftp_file, 'w') as ftp_f:
            csv_writer = csv.DictWriter(ftp_f, fieldnames=ftp_fields)
            csv_writer.writerows(parsed_result.hlr_records)
        hlr3_file = os.path.join(default_settings.hlr_directory, georgia_settings.file_prefix,
                                 f'{georgia_settings.file_prefix}.csv')

        with open(hlr3_file, 'w') as hlr_f:
            csv_writer = csv.DictWriter(hlr_f, fieldnames=hlr3_fields)
            csv_writer.writerows(parsed_result.hlr3_records)


class KazakhstanFileHandler:

    def get_file(self) -> str:
        ftp = ftplib.FTP()
        try:
            ftp.connect(host=kazakhstan_settings.ftp_server, port=kazakhstan_settings.ftp_port)
            ftp.login(user=kazakhstan_settings.ftp_user, passwd=kazakhstan_settings.ftp_password)
        except TimeoutError as err:
            logger.error(f'could not connect to {georgia_settings.ftp_server}:{georgia_settings.ftp_port}')
            raise GetFileError()

        latest_file = get_latest_file_from_ftp(ftp)
        zip_file = download_file(latest_file, ftp)
        ftp.quit()
        with ZipFile(zip_file, 'r') as zip_f:
            raw_mnp_file_name = zip_f.namelist()[0]
            raw_mnp_file = os.path.join(default_settings.tmp_directory, raw_mnp_file_name)
            zip_f.extract(raw_mnp_file_name, default_settings.tmp_directory)
        os.remove(zip_file)
        logger.info(f'extracted {raw_mnp_file}')
        logger.info(f'remove zip file: {zip_file}')
        return os.path.join(default_settings.tmp_directory, raw_mnp_file_name)

    def save_parse_result(self, parsed_result: ParseResult) -> None:
        logger.info('start save parse result')

        hlr3_fields = ('dnis', 'mccmnc', 'active_from', 'ownerID', 'providerResponseCode')
        ftp_fields = ('dnis', 'mccmnc')

        ftp_file = os.path.join(default_settings.ftp_directory, georgia_settings.file_prefix,
                                f'{kazakhstan_settings.file_prefix}.csv')
        logger.info(f'saving ftp file to: {ftp_file}')
        with open(ftp_file, 'w') as ftp_f:
            csv_writer = csv.DictWriter(ftp_f, fieldnames=ftp_fields, delimiter=';')
            csv_writer.writerows(parsed_result.hlr_records)

        hlr3_file = os.path.join(default_settings.hlr_directory, kazakhstan_settings.file_prefix,
                                 f'{kazakhstan_settings.file_prefix}.csv')
        logger.info(f'saving hlr3 file to: {hlr3_file}')
        with open(hlr3_file, 'w') as hlr_f:
            csv_writer = csv.DictWriter(hlr_f, fieldnames=hlr3_fields, delimiter=';')
            csv_writer.writerows(parsed_result.hlr3_records)


class BelarusFileHandler:

    def get_file(self) -> str:
        files = os.listdir(belarus_settings.source_directory)
        logger.info(f'file list: {len(files)}')
    
        if not files:
            logger.warning(f'file not found in source directory: {belarus_settings.source_directory}')
            raise GetFileError

        if len(files) > 1:
            logger.warning(f'to many files in source directory: {belarus_settings.source_directory}')
            raise GetFileError
        source_file = os.path.join(belarus_settings.source_directory, files[0])
        logger.info(f'source mnp file: {source_file}')
        return source_file

    def save_parse_result(self, parsed_result: ParseResult) -> None:
        logger.info('start save parse result')

        hlr3_fields = ('dnis', 'mccmnc', 'active_from', 'ownerID', 'providerResponseCode')
        ftp_fields = ('dnis', 'mccmnc')

        ftp_file = os.path.join(default_settings.ftp_directory, belarus_settings.file_prefix,
                                f'{belarus_settings.file_prefix}.csv')
        logger.info(f'saving ftp file to: {ftp_file}')
        with open(ftp_file, 'w') as ftp_f:
            csv_writer = csv.DictWriter(ftp_f, fieldnames=ftp_fields, delimiter=';')
            csv_writer.writerows(parsed_result.hlr_records)

        hlr3_file = os.path.join(default_settings.hlr_directory, belarus_settings.file_prefix,
                                 f'{belarus_settings.file_prefix}.csv')
        logger.info(f'saving hlr3 file to: {hlr3_file}')
        with open(hlr3_file, 'w') as hlr_f:
            csv_writer = csv.DictWriter(hlr_f, fieldnames=hlr3_fields, delimiter=';')
            csv_writer.writerows(parsed_result.hlr3_records)


def join_all_files():
    logger.info('Start joining all files')
    full_file = default_settings.full_hlr_file
    hlr3_records = []
    for country in AvailableCountry:
        prefix = get_country_prefix(country)
        hlr3_file = os.path.join(default_settings.hlr_directory, prefix, f'{prefix}.csv')
        with open(hlr3_file, 'r') as hlr3_file:
            hlr3_records.extend(hlr3_file.readlines())

    with open(full_file, 'w') as full_hlr_file:
        full_hlr_file.writelines(hlr3_records)
    logger.info('Finish joining all files')


def get_file_handler(country: AvailableCountry) -> FileHandler:
    match country:
        # case country.Georgia:
        #     return GeorgiaFileHandler()
        # case country.Kazakhstan:
        #     return KazakhstanFileHandler()
        case country.Belarus:
            return BelarusFileHandler()
        case _:
            pass
