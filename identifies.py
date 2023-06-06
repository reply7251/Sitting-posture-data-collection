



CONFIG_PATH = "config.ini"

CONFIG_WIFI = "wifi"
CONFIG_WIFI_SSID = "ssid"
CONFIG_WIFI_PWD = "password"

CONFIG_POSTURES = "postures"

CONFIG_FILES = "files"
CONFIG_FILES_SAVE = "save_file"

DEFAULT_CONFIG = {
    CONFIG_POSTURES: {},
    CONFIG_FILES: {
        CONFIG_FILES_SAVE: "record.csv"
    },
    CONFIG_WIFI: {
        CONFIG_WIFI_SSID: "",
        CONFIG_WIFI_PWD: ""
    }
}


SERIAL_DATA_NUMERIC = "numeric"
SERIAL_DATA_STRING = "string"
SERIAL_DATA_TYPE = "type"
SERIAL_DATA_TYPE_EXIT = "exit"
SERIAL_DATA_TYPE_DATA = "data"