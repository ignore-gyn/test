# -*- coding: utf-8 -*-
import time
import pyparsing as pp
import logging


def test(msg_pattern):
    samples = []

    samples.append('''
    S2F15
    <L> .

    headeronly: 'S1F1' W.
    headeronly2: 'S1F2'.
    S6F11 W

    .
    S6F12.

    simple: 'S2F14'
    <L
        <A 100>
        <A "tes
        afaef
        000000000000
        t1">
    > .

    secondsdf: 'S2F14'
    <L
        <A "abc">
        <L
            <L
                <U4 1 10 123>
                <L>
            >
            <U4 3>
        >
    > .

    S2F15 W
    <L
        <A 100>
        <A "test">
        <A "commnet/* end */hello">
        <U4 200 10 12> // commnet
        <F4 3.14 >
        <B 10>
    //    <B 100 0x54 3>
        <U4 >
        <L>
        <L <L<U4 1> <L>> <U4 3> >
    > .

    afeadf: 'S2F15' W
    <L
        <A "tests1 test2"> /* commnet */
        <A>
        <U4 200 10 12>
/*        <U4 >
        <L> */
        <L <L/*<U4 1> <L>*/> <U4 3> >
    > .

    ''')

    samples.append("""
    hello1243oafepo:'S1F3'
    <A 100 200>.
    """)

    samples.append("""
    wtihlen:'S1F3'
    <A[20000] 100 200>.
    """)

    samples.append('''
    S1F1
    <A 100>
    <L <U4 3> >.
    ''')

    samples.append('''
    S1F1
    <L><L> .
    ''')

    samples.append("""
    test6:'S1F3'
    <L
        <U4 100 200>
        <B 5 6 7>
        <A[3] 0x41 0x42 0x43>
        <A[3] 0xaa 0xbb 0xcc>
        <A[3] "aefa+*;a!#%$&">
    > .
    """)

    for i, s in enumerate(samples, 1):
        print "=" * 80
        try:
            result = msg_pattern.parseString(s)
        except pp.ParseException as e:
            print "result", i, ": match failed"
            print "    rason:", e
            continue

        print "result", i, ":", result

        output_msg(result)


def output_msg(msglist):
    for msg in msglist:
        print "-" * 60
        part_count = len(msg)
        if isinstance(msg[-1], pp.ParseResults):
            part_count = part_count - 1

        if part_count == 3:
            msgname = msg[0]
            sf = msg[1]
            wbit = True
        elif part_count == 2:
            if msg[1] == "W":
                msgname = ""
                sf = msg[0]
                wbit = True
            else:
                msgname = msg[0]
                sf = msg[1]
                wbit = False
        elif part_count == 1:
            msgname = ""
            sf = msg[0]
            wbit = False
        else:
            print "ParseError: (MeesageName), SF, (Wbit) are not retrieved correctly:",
            msg[0:part_count]
            continue

        print "MsgName=[", msgname, "], SF=[", sf, "], Wbit=[", wbit, "]"
        print

        if isinstance(msg[-1], pp.ParseResults):
            parse_item(msg[-1], 0)


TAB = "    "


def parse_list(item, indent_count):
    tab_str = TAB * indent_count
    if item[0] == "L":
        if len(item) == 1:
            print "%s<L[0]>" % (tab_str)
        else:
            print "%s<L[%d]" % (tab_str, len(item) - 1)
            for i in item[1:]:
                if not parse_item(i, indent_count + 1):
                    return False
            print "%s>" % (tab_str)

        return True
    else:
        print "ParseError: Invalid List Item (type=%s): %s" % (
            item[0], item[1:])
        return False
        # parse_item(item)

import string

def parse_item(item, indent_count):
    tab_str = TAB * indent_count
    try:
        if item[0] == "L":
            if not parse_list(item, indent_count):
                return False

        elif item[0] == "A":

            if len(item) == 1:
                print "%s<A[0]>" % (tab_str)
            elif len(item) == 2 and isinstance(item[1], str):
                print '%s<A[%d] "%s">' % (tab_str, len(item[1]), item[1])            
            else:
                printable_char_set = set(map(ord, string.printable))
                vlist = item[1:]
                # s = map(chr, vlist)
                isprintable = set(vlist).issubset(printable_char_set)
                if isprintable:
                    print '%s<A[%d] "%s">' % (tab_str, len(vlist), "".join(map(chr, vlist)))
                else:
                    print "%s<A[%d] %s>" % (tab_str, len(vlist), " ".join(["0x%02X" % v for v in vlist]))
            
        elif item[0] == "F4":
            if len(item) > 1:
                vlist = item[1:]
                print "%s<%s[%d] %s>" % (tab_str, item[0], len(
                    vlist), " ".join(["%f" % v for v in vlist]))
            else:
                print "%s<%s[0]>" % (tab_str, item[0])

        else:
            if len(item) > 1:
                vlist = item[1:]
                if item[0] == "B" or item[0] == "BOOLEAN":
                    print "%s<%s[%d] %s>" % (tab_str, item[0], len(
                        vlist), " ".join(["0x%02X" % v for v in vlist]))
                else:
                    print "%s<%s[%d] %s>" % (tab_str, item[0], len(
                        vlist), " ".join(["%d" % v for v in vlist]))
            else:
                print "%s<%s[0]>" % (tab_str, item[0])

        return True

    except ValueError:
        print "ParseError: Invalid Value for type=%s: %s" % (item[0], item[1])
        return False


# def compose_pattern():
#     # SF, wbit and name expression
#     sf = pp.Regex(r"S\d+F\d+")

#     colon = pp.Suppress(':')
#     quote = pp.Suppress("'")
#     sf_name = pp.OneOrMore(pp.CharsNotIn(":\r\n"))
#     sf_with_name = sf_name + colon + quote + sf + quote

#     msg_head = (sf | sf_with_name) + pp.Optional('W')

#     # Body expression
#     start_bracket = pp.Suppress("<")
#     end_bracket = pp.Suppress(">")

#     item_length = pp.Regex(r"\[\d+\]").suppress()
#     item_type = pp.MatchFirst(["A", "BOOLEAN", "B",
#                                "U1", "U2", "U4",
#                                "I1", "I2", "I4",
#                                "F4"]) + pp.Optional(item_length)
#     list_type = pp.Literal("L") + pp.Optional(item_length)

#     numeric_val = pp.Regex(r"([0-9a-fA-FxX\-\.]+ ?)+")
#     string_val = pp.QuotedString(
#         quoteChar='"',
#         multiline=True,
#         unquoteResults=False)
#     value_data = (string_val | numeric_val) + pp.FollowedBy(">")

#     item_data = start_bracket + item_type + \
#         pp.Optional(value_data) + end_bracket
#     list_item_data = pp.Forward()
#     list_item_data << start_bracket + list_type + \
#         pp.ZeroOrMore(pp.Group(item_data | list_item_data)) + end_bracket

#     msg_body = list_item_data | item_data

#     # Combine all expressions
#     msg_pattern = pp.ZeroOrMore(pp.Group(
#         msg_head +
#         pp.Optional(pp.Group(msg_body)) +
#         pp.Suppress(".")))
#     msg_pattern.ignore(pp.cppStyleComment)

#    return msg_pattern


def compose_pattern2():
    # SF, wbit and name expression
    sf = pp.Regex(r"S\d+F\d+")

    colon = pp.Suppress(':')
    quote = pp.Suppress("'")
    sf_name = pp.OneOrMore(pp.CharsNotIn(":\r\n"))
    sf_with_name = sf_name + colon + quote + sf + quote

    msg_head = (sf | sf_with_name) + pp.Optional('W')

    # Body expression
    start_bracket = pp.Suppress("<")
    end_bracket = pp.Suppress(">")

    item_length = pp.Regex(r"\[\d+\]").suppress()

    float_val = pp.OneOrMore(pp.Regex(
        r"([0-9\-\.]+?)+")).setParseAction(pp.tokenMap(float))
    float_item = pp.Literal("F4") + pp.Optional(item_length) + pp.Optional(float_val) + pp.FollowedBy(">")

    int_val = pp.OneOrMore(pp.Regex(
        r"([0-9a-fA-FxX\-]+?)+")).setParseAction(pp.tokenMap(int, 0))
    int_item = pp.oneOf("BOOLEAN B U1 U2 U4 I1 I2 I4 A") + pp.Optional(item_length) + pp.Optional(int_val) + pp.FollowedBy(">")

    string_val = pp.QuotedString(
        quoteChar='"',
        multiline=True,
        unquoteResults=True).setParseAction(lambda s: [ord(x) for x in s[0]])
    string_item = pp.Literal("A") + pp.Optional(item_length) + pp.Optional(string_val) + pp.FollowedBy(">")

    item_data = start_bracket + (string_item | float_item | int_item) + end_bracket
    
    list_type = pp.Literal("L") + pp.Optional(item_length)
    list_item_data = pp.Forward()
    list_item_data << start_bracket + list_type + pp.ZeroOrMore(pp.Group(item_data | list_item_data)) + end_bracket

    msg_body = list_item_data | item_data

    # Combine all expressions
    msg_pattern = pp.ZeroOrMore(pp.Group(
        msg_head +
        pp.Optional(pp.Group(msg_body)) +
        pp.Suppress(".")))
    msg_pattern.ignore(pp.cppStyleComment)

    return msg_pattern


def init_logger():
    logger = None
    logger = logging.getLogger()
    logger.setLevel(0)
    handler = logging.StreamHandler()
    handler.setLevel(0)
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(message)s",
        "%y/%m/%d %H:%M:%S"
    ))
    logger.addHandler(handler)

    for i in range(0, 30):
        logger.error("hello")
        time.sleep(0.3)


if __name__ == "__main__":

    pattern = compose_pattern2()
    test(pattern)
