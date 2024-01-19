from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class LoggerSettings(BaseSettings):
    log_level: str = Field(env="LOG_LEVEL", default="INFO")
    log_dir: str = Field(env="LOG_DIRECTORY", default="logs")
    log_filename: str = Field(env="LOG_FILENAME")
    log_format: str = Field(env="LOG_FORMAT", default="%(asctime)s - %(levelname)s - %(message)s")


class Settings(BaseSettings):
    tmp_directory: str = Field(validation_alias='TMP_DIRECTORY')
    ftp_directory: str = Field(validation_alias='FTP_DIRECTORY')
    hlr_directory: str = Field(validation_alias='HLR_DIRECTORY')
    archive_dir: str = Field(validation_alias='ARCHIVE_DIRECTORY')
    full_hlr_file: str = Field(validation_alias='FULL_HLR_FILE')
    smssw_server: str = Field(validation_alias='SMSSW_SERVER')
    smssw_user: str = Field(validation_alias='SMSSW_SERVER_USER')
    smssw_full_hlr_file_path: str = Field(validation_alias='SMSSW_FULL_HLR_FILE_PATH')


class GeorgiaMnpSettings(BaseSettings):
    ftp_server: str = Field(validation_alias='GEORGIA_FTP_SERVER')
    ftp_port: int = Field(validation_alias='GEORGIA_FTP_PORT')
    ftp_user: str = Field(validation_alias='GEORGIA_FTP_USER')
    ftp_password: str = Field(validation_alias='GEORGIA_FTP_PASSWORD')
    file_prefix: str = 'georgia'


class KazakhstanMnpSettings(BaseSettings):
    ftp_server: str = Field(validation_alias='KAZAKHSTAN_FTP_SERVER')
    ftp_port: int = Field(validation_alias='KAZAKHSTAN_FTP_PORT')
    ftp_user: str = Field(validation_alias='KAZAKHSTAN_FTP_USER')
    ftp_password: str = Field(validation_alias='KAZAKHSTAN_FTP_PASSWORD')
    file_prefix: str = 'kazakhstan'


class BelarusMnpSettings(BaseSettings):
    source_directory: str = Field(validation_alias='BELARUS_SOURCE_DIRECTORY')
    file_prefix: str = 'belarus'


default_settings = Settings()
log_settings = LoggerSettings()
georgia_settings = GeorgiaMnpSettings()
kazakhstan_settings = KazakhstanMnpSettings()
belarus_settings = BelarusMnpSettings()