import re

### Config ###
ASCII_TRANS = True
DEVID_OMIT = True
VID_TRANS_RULE = "0:1,3:4,*:5,[10 20]:[4 5],0x0f:0x06,[0x01 0x2]:[0x3 0x4]"
POS_TRANS_RULE = "[9 8]:[10 20],0x10:0x0f,[0xFF 0xAB]:[0x1 0x2]"

H_vid_trans_dict = {}
E_vid_trans_dict = {}
H_pos_trans_dict = {}
E_pos_trans_dict = {}

### Const Value ###
IN = "IN"
OUT = "OUT"

TYPE_A = "A"
TYPE_B = "B"
TYPE_BOOLEAN = "BOOLEAN"
TYPE_I = "I"
TYPE_U = "U"
TYPE_F = "F"

### Regex ###
input_pat = "(.+)<([A-Z124]+) (.+)>"

def get_decimal_string(hexstr):
    if hexstr[0] == "[" and hexstr[-1] == "]":
        data = hexstr[1:-1]
    else:
        data = hexstr
    
    out = ""
    for d in data.split(" "):
        try:
            if "0x" in d:
                out += "%d " % int(d, 0)
            else:
                out += "%d " % int(d, 10)
        except:
            out = ""
            break
    
    if out:
        out = out[:-1]

    if hexstr[0] == "[" and hexstr[-1] == "]":
        out = "[" + out + "]"
    
    return out

def conv_value(table, fmt, value):
    # A: Strip "" -> Conv -> Add ""
    # not A: If array, add "[]" -> Conv -> If array, strip "[]"

    hex_table = table

    if fmt == TYPE_A:
        if value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
    elif " " in value:
        value = "[" + value + "]"

    if fmt == TYPE_B:
        hex_value = get_decimal_string(value)


    res = table.get(value)
    if not res:
        if fmt == TYPE_B:
            for r in hex_table:
                if hex_value == get_decimal_string(r):
                    res = get_decimal_string(hex_table[r])
                    break
        
        if not res:
            res = table.get("*")
            if not res:
                return None
            elif fmt == TYPE_B:
                res = get_decimal_string(res)
    
    if fmt == TYPE_A:
        return '"' + res + '"'
    else:
        if value.count(' ') == res.count(' '):
            if res[0] == "[" and res[-1] == "]":
                res = res[1:-1]
            return res
        else:
            return None


def in_value_trans_vid(item):
    if not item:
        return item

    fmt = item[0]
    value = item[1]

    res = conv_value(H_vid_trans_dict, fmt, value)
    if res:
        value = res

    return (fmt, value)

def out_value_trans_vid(item):
    if not item:
        return item

    fmt = item[0]
    value = item[1]

    res = conv_value(E_vid_trans_dict, fmt, value)
    if res:
        value = res

    return (fmt, value)

def in_ascii_value_trans(item):
    if not item:
        return item

    fmt = item[0]
    value = item[1]

    if fmt != TYPE_A:
        if ASCII_TRANS:
            value = value.replace(",", " ")

    res = conv_value(H_pos_trans_dict, fmt, value)
    if res:
        value = res

    return (fmt, value)

def out_ascii_value_trans(item):
    if not item:
        return item

    fmt = item[0]
    value = item[1]

    res = conv_value(E_pos_trans_dict, fmt, value)
    if res:
        value = res
    
    if fmt != TYPE_A:
        if ASCII_TRANS:
            value = '"' + value.replace(" ", ",") + '"'
            fmt = TYPE_A

    return (fmt, value)

def omit_deviceid(item):
    if not item:
        return item
    if item[0] != TYPE_A:
        return item

    value = item[1]
    i = value.rfind(r"/")
    if i > -1:
        value = '"' + value[i+1:]

    return (item[0], value)


def trans(direction, item):
    original_fmt = item[0]

    if direction == IN:
        # Host | -> | SECS2 | -> | DEV | -> | VAR | -> | GDMS
        separator = " ---> "
        if ASCII_TRANS:
            if original_fmt != TYPE_A:
                item0 = '<A "%s">' % item[1]
            else:
                item0 = '<%s %s>' % (item[0], item[1])
        else:
            item0 = '<%s %s>' % (item[0], item[1])
        
        item = in_ascii_value_trans((original_fmt, item[1]))
        item1 = "<%s %s>" % (item[0], item[1])
        item2 = ""
        item = in_value_trans_vid(item)
        item3 = "<%s %s>" % (item[0], item[1])
        
        out = separator + (separator).join([item0, item1, item2, item3])
        return out

    elif direction == OUT:
        # Host | <- | SECS2 | <- | DEV | <- | VAR | <- | GDMS
        separator = " <--- "
        item0 = "<%s %s>" % (item[0], item[1])

        item = out_value_trans_vid(item)
        item1 = "<%s %s>" % (item[0], item[1])
        item = omit_deviceid(item)
        item2 = "<%s %s>" % (item[0], item[1])
        item = out_ascii_value_trans(item)
        item3 = "<%s %s>" % (item[0], item[1])

        out = separator + (separator).join([item3, item2, item1, item0])
        return out

    else:
        print "Error: Direction[%s]" % direction
        return None

def main():
    pat = re.compile(input_pat)

    if VID_TRANS_RULE:
        rule = VID_TRANS_RULE.split(",")
        for r in rule:
            s = r.split(":")
            if s[0] == "*":
                H_vid_trans_dict[s[0]] = s[1]
            elif s[1] == "*":
                E_vid_trans_dict[s[1]] = s[0]
            else:
                H_vid_trans_dict[s[0]] = s[1]
                E_vid_trans_dict[s[1]] = s[0]

    if POS_TRANS_RULE:
        rule = POS_TRANS_RULE.split(",")
        for r in rule:
            s = r.split(":")
            if s[0] == "*":
                H_pos_trans_dict[s[0]] = s[1]
            elif s[1] == "*":
                E_pos_trans_dict[s[1]] = s[0]
            else:
                H_pos_trans_dict[s[0]] = s[1]
                E_pos_trans_dict[s[1]] = s[0]

    while True:
        print "input >>",
        in_item = raw_input()
        if in_item == "q":
            break
        else:
            result = pat.match(in_item)
            if result:
                direction = result.group(1)
                item = (result.group(2), result.group(3))
                out_item = trans(direction, item)
                if out_item:
                    print "HOST ---- SECS2 ---- DevID ---- VID ---- GDMS"
                    print out_item
                else:
                    print "Conversion Error"
            else:
                print "Invalid Input"


if __name__ == "__main__":
  main()