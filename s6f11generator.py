# -*- coding: utf-8 -*-

log = """<L
    <U4 1001>
    <U4 9999>
    <L
        <L
            <U4 1001>
            <L
                <L>
                <L
                    <L
                        <A "abc">
                    >
                    <U4 123>
                >
                <A "test">
                <U4 987>
            >
        >
        <L
            <U4 1002>
            <L>
        >
        <L

            <U4 1003>
            <L
                <L
                    <L
                        <L>
                    >
                >
                <A "lkjo">
                <U4 123>
                <L>
            >
        >
    >
>"""
# CEID - EVENTNAME
event_list = {
              9991 : "Event1",
              9999 : "Event2"
              }

# RPTID - VIDs
report_list = {
              1004 : [1, 2, 3],
              1002 : [1, 2, 3],
              1003 : [4, 2, 3,5],
              1005 : [1, 2, 3],
              1001 : [4, 5, 6, 9],
    }
# VID - VNAME
var_list = {
            1 : "var1",
            2 : "var2",
            3 : "var3",
            4 : "var4",
            5 : "var5",
            6 : "var6",
            7 : "var7",
            }

# rfindでも先頭インデクスが返ることに注意

class s6f11:

    def __init__(self):
        self.ceid = None
#         self.report_list = None
        self.current_rptid = None
        self.tmp_varname = ""

    def notifyItem(self, item, digest):
        depth = item["depth"]

        # CEID
        if len(depth) == 2 and depth[1] == 2:
            ceid = int(item["value"])
            digest["detail"] += "%s// %s\n" %\
                                (item["line"].ljust(32, ' '), event_list[ceid])

        # RPTID
        elif len(depth) == 4 and depth[3] == 1:
            self.current_rptid = int(item["value"])
            digest["detail"] += item["line"] + '\n'

        # VarTop (non-L or 0-length L)
        elif len(depth) == 5 and depth[4] > 0:
            vid = report_list[self.current_rptid][depth[4]-1]
            var_name = var_list.get(vid)

            if var_name is not None:
                digest["detail"] += item["line"].ljust(32, ' ') + '// %d %s\n' % (vid, var_name)

            if item["value"] is not None:
                if digest["value"] != "":
                    digest["value"] += ', '
                digest["value"] += '%s: %s' % (var_name, str(item["value"]))
            self.tmp_varname = ""

        # VarTop (L)
        elif len(depth) == 6 and depth[5] == 0:
            vid = report_list[self.current_rptid][depth[4]-1]
            var_name = var_list.get(vid)

            if var_name is not None:
                digest["detail"] += item["line"].ljust(32, ' ') + '// %d %s\n' % (vid, var_name)

            # 中身が何もない可能性があるので、ここでは変数名を"value"にいれない
            self.tmp_varname = var_name

        # Value in L
        elif len(depth) >= 6 and depth[5] > 0:
            if item["value"] is not None:
                # First Value
                if self.tmp_varname != "":
                    if digest["value"] != "":
                        digest["value"] += ', '
                    digest["value"] += "%s: %s" % (self.tmp_varname, str(item["value"]))
                    self.tmp_varname = ""

                # Second or after Value
                else:
                    digest["value"] += " | %s" % str(item["value"])

            digest["detail"] += item["line"] + '\n'

        else:
            digest["detail"] += item["line"] + '\n'

if __name__ == '__main__':

    readable_depth =[0]
    msg = s6f11()

    digest = {
              "value" : "",
              "detail" : ""
              }

    for line in log.splitlines(): # 改行を残す場合はTrueに
        if len(readable_depth) == 0:
            break

        item = {
                "depth" : [],
                "type" : None,
                "value" : None,
#                 "length" : None
                "line" : line
                }

        if line.find('<L') > -1:
            readable_depth[-1] += 1
            if line.find('>') == -1:    # <L>じゃないことを確認
                readable_depth.append(0)

            item["depth"] = readable_depth
            item["type"] = "L"
            item["value"] = None

        elif line.find('<') > -1:
            readable_depth[-1] += 1

            item["depth"] = readable_depth
            space_pos = line.rfind(' ')
            if space_pos == -1:
                item["type"] = line[line.find('<')+1: line.rfind('>')]
                item["value"] = None
            else:
                item["type"] = line[line.find('<')+1: space_pos]
                item["value"] = line[space_pos+1: line.rfind('>')]

        elif line.find('>') > -1:
            readable_depth.pop()
            print line.ljust(40, ' ') + " # depth=" + str(readable_depth)
            digest["detail"] += line + '\n'
            continue

        print line.ljust(40, ' ') + " # depth=" + str(readable_depth)
        msg.notifyItem(item, digest)

    print "\n%s\n" % ('#' * 40)
    print digest["detail"]
    print "\n%s\n" % ('#' * 40)
    print digest["value"]

#####
"""
【今】
②log_parserに1メッセージごとにパースさせる
②パース結果から、ダイジェスト対象か判定(SF&time)
③digest_generatorにダイジェスト情報を生成させる

【案】
chsms_log_parserからLEN, HDRのイベント(property)を上げる
①odmでLENイベントに対して、時間が対象か判定する
②odmでHDRイベントに対して、ダイジェスト対象か判定し、
    対象のsxfy_digest_generatorをインスタンス化
    インスタンスをchsms_log_parserへ渡す
③MSGのアイテムごとに、sxfy_digest_generatorにannotation, digest valueを生成させる
    S6F11の場合は、CEIDに遭遇し次第ダイジェスト対象か判定し、
    対象でなかった場合は、パースをとばす
④odmでMessageEndイベントに対して、digest情報を受け取り、ファイルへ出力する


"""
####
