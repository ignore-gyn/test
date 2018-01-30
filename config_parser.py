# -*- coding: utf-8 -*-
import json
import os

GDMS = "gdms"
DEST_PATH = "dest_path"
CHSMS_FILE_LIST = "chsms_file_list"
SF_LIST = "sf_list"
CEID_FILTER = "ceid_filter"
ENABLE_LOG = "enable_log"

default_config = {
                  GDMS:"gdms.csv",
                  DEST_PATH: "./hoge/",
                  CHSMS_FILE_LIST: ["a.txt"],
                  SF_LIST: ["S1F2", "S6F11"],
                  CEID_FILTER: {},
                  ENABLE_LOG: "True"
                  }

class ConfigParser(object):
    def __init__(self):

        self.invalid_items = []
        self.status_code = 0
        self.status_message = []

        try:
            f = open('config.json')
            self.json_data = json.load(f)
        except:
            self.status_message.append("Unable to read config file")
            self.status_code = 200
            self.json_data = default_config

        self.gdms = self.__check_gdms()
        self.dest = self.__check_dest()
        self.chsms_list = self.__check_chsms_list()
        self.sf_list = self.__check_config_item(SF_LIST, list)
        self.enable_log =  self.__check_enable_log()

        """
        1. [%s] is not specified or invalid format. Using default config.
        2. Unable to read config file
        3. Unable to read xxx file
        4. Unable to read chsms file / Unable to read all chsms files

        1, 2は共存しない
        """

        if self.invalid_items:
            message = "[%s] is not specified or invalid format. Using default config." % ', '.join(self.invalid_items)
            self.status_message = [message] + self.status_message
            # self.status_message.insert(0, message)

            # 0: OK, 100: WARN, 200: ERR
            if self.status_code < 100:
                self.status_code = 100

        if not self.status_message:
            self.status_message = ["OK"]
        # status code == 100 (CHSMSファイルがないか、出力先が作れなかったか)だった場合すぐに終了したい

    def __check_config_item(self, config_item_name, config_item_type):

        item_data = self.json_data.get(config_item_name)
        if item_data is None or not isinstance(item_data, config_item_type):

            self.invalid_items.append('"%s"' % config_item_name)
#             print '"%s" is not specified or invalid format. Using default config.' % config_item_name
            item_data = default_config[config_item_name]

        return item_data

    def __check_gdms(self):
        gdms = self.__check_config_item(GDMS, unicode)

        if not os.path.exists(gdms):
            self.status_message.append("Unable to read gdms file")
            self.status_code = 200
            gdms = None

        return gdms

    def __check_dest(self):
        dest = self.__check_config_item(DEST_PATH, unicode)

        try:
            if not os.path.exists(dest):
                os.mkdir(dest)
        except:
            # これが発生したら終了するしかないんだが
            self.status_message.append("Failed to create output dest")
            self.status_code = 100
            dest = None

        return dest

    def __check_chsms_list(self):
        chsms_files = self.__check_config_item(CHSMS_FILE_LIST, list)
        valid_chsms_files = []

        for f in chsms_files:
            if os.path.exists(f):
                valid_chsms_files.append(f)

        if not valid_chsms_files:
            self.status_message.append("Unable to read all chsms files")
            self.status_code = 200
        elif len(chsms_files) != len(valid_chsms_files):
            self.status_message.append("Unable to read chsms file")
            self.status_code = 100

        return valid_chsms_files

    def __check_enable_log(self):
        enable_log = self.__check_config_item(ENABLE_LOG, unicode)

        if enable_log == "False":
            return False
        else:
            return True

if __name__ == '__main__':

    config_parer = ConfigParser()

    print config_parer.status_code
    print '\n'.join(config_parer.status_message)




