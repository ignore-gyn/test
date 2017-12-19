# -*- coding: utf-8 -*-
import sys

LEN = 0
HDR = 1
MSG = 2

from time import sleep

class NewError(Exception):
    pass

def get_next_line():
    file_list = ["./data/bin1.txt", "./data/bin2.txt"]
    status = None
    lines = []
    is_new_file = False

    for file_path in file_list:
        try:
            f = open(file_path)
        except IOError:
            sys.exit(1)

        for l in f:
            if "[LEN]" in l:
                if status == "MSG":
                    yield lines, status, is_new_file

                status = "LEN"
                yield l, status, is_new_file

            elif "[HDR]" in l:
                if status == "MSG":
                    yield lines, status, is_new_file

                is_new_file = False
                status = "HDR"
                yield l, status, is_new_file

            elif "[MSG]" in l:
                if status == "MSG":
                    yield lines, status, is_new_file

                is_new_file = False
                status = "MSG"
                lines = [l]

            else:
                if status == "MSG":
                    lines.append(l)

        if status == "MSG":
            yield lines, status, is_new_file

        f.close()
        print file_path + " Closed."
        is_new_file = True

#     except IOError:
#         pass
#     except StopIteration:
#         yield "", "EOF"


def get_next_line2():
    file_list = ["./data/bin1.txt", "./data/bin2.txt"]
    status = None
    lines = []

    for file_path in file_list:
        try:
            f = open(file_path)
        except IOError:
            print "Failed to open " + file_path
            return  # raise StopIteration

        for l in f:
            if "[LEN]" in l:
                if status == "MSG":
                    yield lines, status

                status = "LEN"
                yield l, status

            elif "[HDR]" in l:
                if status == "MSG":
                    yield lines, status

                status = "HDR"
                yield l, status

            elif "[MSG]" in l:
                if status == "MSG":
                    yield lines, status

                status = "MSG"
                lines = [l]

            else:
                if status == "MSG":
                    lines.append(l)

        # メッセージがファイルをまたぐことはない
        if status == "MSG":
            yield lines, status
            status = None

        f.close()
        print file_path + " Closed."


if __name__ == '__main__':

    reader = get_next_line2()

    try:
        for lines, status in reader:    # StopIteration出ない
#         while True:
#             lines, status = reader.next()
            print status
            if status == "MSG":
                lines = ''.join(lines).replace('\n', '').replace(' ', '')
            print lines

    except StopIteration:
        print "EOF"


