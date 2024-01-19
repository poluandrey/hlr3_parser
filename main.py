import os

from config import default_settings
from error.errors import GetFileError
from logger_config import configure_logger
from file_handlers.file_handler import get_file_handler, join_all_files
from parsers.parser import get_parser, AvailableCountry
from utils import archive_file, push_file_to_server

logger = configure_logger(__name__)


def main() -> None:
    logger.info("starting main application")
    for country in AvailableCountry:

        try:
            logger.info(f"starting handling country: {country.name}")
            parser = get_parser(country)
            file_handler = get_file_handler(country)
            try:
                raw_mnp_file = file_handler.get_file()
            except GetFileError:
                logger.error('Could not get source mnp file')
                break
            except AttributeError:
                logger.exception('Could not get source mnp file')
                break
            parse_result = parser.parse(raw_mnp_file)
            if len(parse_result.hlr_records) == 0 or len(parse_result.hlr3_records) == 0:
                logger.error('one of parsed hlr format is empty')
                break

            archive_file(raw_mnp_file, country.name)
            logger.debug(f'remove raw mnp file: {raw_mnp_file}')
            os.remove(raw_mnp_file)

            file_handler.save_parse_result(parse_result)
        except Exception as e:
            logger.exception(e, exc_info=True)
            pass
        finally:
            logger.info(f"finished handling country: {country.name}")

    logger.info("Archive full hlr file")
    archive_file(default_settings.full_hlr_file, 'full_hlr')
    join_all_files()
    push_file_to_server(default_settings.smssw_server,
                        22,
                        default_settings.full_hlr_file,
                        default_settings.smssw_full_hlr_file_path)


def main_test():
    file_handler = get_file_handler(country=AvailableCountry.Belarus)
    raw_mnp_file = file_handler.get_file()
    parser = get_parser(country=AvailableCountry.Belarus)
    parse_result = parser.parse(raw_mnp_file)
    archive_file(raw_mnp_file, AvailableCountry.Belarus.name)
    os.remove(raw_mnp_file)
    file_handler.save_parse_result(parse_result)


if __name__ == '__main__':
    main()
    # main_test()
