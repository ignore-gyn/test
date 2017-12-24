# -*- coding: utf-8 -*-
import sys

LEN = 0
HDR = 1
MSG = 2

OK = 1
NG = 0
END_OF_MESSAGE = 2

class ThreadInfo(object):
    def __init__(self):
        self.threads = {}

    def clear(self, threadid):
        if self.threads.get(threadid) is not None:
            self.threads[threadid].__init__()

    def add_LEN(self, threadid, info):
        print "add_LEN:" + str(threadid)
        if self.threads.get(threadid) is None:
            self.threads[threadid] = Message()
        else:
            self.threads[threadid].__init__()

        message = self.threads[threadid]
        if message.set_LEN_info(info):
            return OK
        else:
            message.__init__()

        return NG

    def add_HDR(self, threadid, info):
        print "add_HDR:" + str(threadid)
        message = self.threads.get(threadid)
        if message is not None:
            if message.set_HDR_info(info):
                return OK
            else:
                message.__init__()

        return NG

    def add_MSG(self, threadid):
        print "add_MSG:" + str(threadid)
        message = self.threads.get(threadid)
        if message is not None:
            return message
        return NG

class Message(object):
    """
    この中で対象のSFかどうかの判定をする
    """

    def __init__(self):
        # from LEN
        self.msg_length = -1
        self.timestamp = None

        # from HDR
        self.sf = None
        self.direction = None

        # from MSG
        self.digest_generator = None
        self.digest_value = None
        self.digest_details = None

    def set_LEN_info(self, info):
        self.msg_length = info.get("length") - 10   # 10 is HDR length
        self.timestamp = info.get("timestamp")

#         if timestamp is out_of_scope:
#             return False
        return OK

    def set_HDR_info(self, info):
        self.sf = info.get("sf")
        self.direction = info.get("direction")

#         if sf is out_of_scope:
#             return False
        return OK

    def set_MSG_info(self, info):
#         if len(info) != self.msg_length:
#             return False

#         digest_generator = generator_factory.get("sf")
#         self.digest_value, self.digest_details = digest_generator().get_digest(info)

        return OK

def get_next_line2():

    file_list = ["./data/bin1.txt", "./data/bin2.txt"]
    status = None
    lines = []
    threadid = None

    for file_path in file_list:
        try:
            f = open(file_path)
        except IOError:
            print "Failed to open " + file_path
            return  # raise StopIteration

        for l in f:
            if "[LEN]" in l:
                if status == "MSG":
                    yield lines, status, threadid

                threadid = int(l[l.rfind("[")+1:l.rfind("]")])
                status = "LEN"
                yield l, status, threadid

            elif "[HDR]" in l:
                if status == "MSG":
                    yield lines, status, threadid

                threadid = int(l[l.rfind("[")+1:l.rfind("]")])
                status = "HDR"
                yield l, status, threadid

            elif "[MSG]" in l:
                if status == "MSG":
                    yield lines, status, threadid


                threadid = int(l[l.rfind("[")+1:l.rfind("]")])
                status = "MSG"
                lines = [l]

            else:
                if status == "MSG":
                    lines.append(l)

        # メッセージがファイルをまたぐことはない
        if status == "MSG":
            yield lines, status, threadid
            status = None

        f.close()
        print file_path + " Closed."


if __name__ == '__main__':


    reader = get_next_line2()

    thread_info = ThreadInfo()

    try:
        x = 0
        for lines, status, threadid in reader:    # StopIteration出ない
            x = x+1
#         while True:
#             lines, status = reader.next()
            if status == "LEN":
                info = {}
                info["length"] = 10
                info["timestamp"] = "abc"
                thread_info.add_LEN(threadid, info)

            elif status == "HDR":
                info = {}
                info["sf"] = x
                info["direction"] = "H->E"
                thread_info.add_HDR(threadid, info)

            elif status == "MSG":
                lines = ''.join(lines).replace('\n', '').replace(' ', '')
                info = {}
                ret = thread_info.add_MSG(threadid)
                print threadid, ret.sf
                thread_info.clear(threadid)

    except StopIteration:
        print "EOF"


