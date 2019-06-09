#!/usr/bin/env python
# -*- coding: utf-8 -*-

C_UP = 127
C_DOWN = -128
S_UP = 32767
S_DOWN = -32768
L_UP = 2147483647
L_DOWN = -2147483648

ZERO = 0
UC_UP = 255
UC_DOWN = ZERO
US_UP = 65535
US_DOWN = ZERO
UL_UP = 4294967295
UL_DOWN = ZERO

var_limits = {
  "BOOLEAN": {"UP": UC_UP, "DOWN": UC_DOWN},
  "B": {"UP": UC_UP, "DOWN": UC_DOWN},
  "U1": {"UP": UC_UP, "DOWN": UC_DOWN},
  "U2": {"UP": US_UP, "DOWN": US_DOWN},
  "U4": {"UP": UL_UP, "DOWN": UL_DOWN},
  "I1": {"UP": C_UP, "DOWN": C_DOWN},
  "I2": {"UP": S_UP, "DOWN": S_DOWN},
  "I4": {"UP": L_UP, "DOWN": L_DOWN},
  "F4": {"UP": 3.14159, "DOWN": -3.1416},
  "A": {"UP": "UP", "DOWN": "DOWN"},
}

var_list = [
  101,
  201,
  202,
  301,
  302,
  304,
  501,
  502,
  504,
  901,
  401
]

rule1 = [
  "#UP",
  "#DOWN 1 #UP"
]
rule2 = [
  "#DOWN",
  "#UP 1 #DOWN"
]


config_rule1 = [
  "#UP:#DOWN",
  "#DOWN:1",
  "*:#UP"
]
config_rule2 = [
  "[#UP 0 #DOWN]:[#DOWN 1 #UP]",
  "[1 #UP #DOWN]:[#DOWN #UP 100]",
  "*:[#UP #DOWN]"
]

var_data_list = {
  101: {"type": "BOOLEAN", "S2F15": rule1, "config": config_rule1},
  201: {"type": "B", "S2F15": rule1, "config": config_rule1},
  202: {"type": "B", "S2F15": rule2, "config": config_rule2},
  301: {"type": "U1", "S2F15": rule1, "config": config_rule1},
  302: {"type": "U2", "S2F15": rule2, "config": config_rule2},
  304: {"type": "U4", "S2F15": rule1, "config": config_rule1},
  501: {"type": "I1", "S2F15": rule1, "config": config_rule1},
  502: {"type": "I2", "S2F15": rule2, "config": config_rule2},
  504: {"type": "I4", "S2F15": rule1, "config": config_rule1},
  901: {"type": "F4", "S2F15": rule1, "config": config_rule1},
  401: {"type": "A", "S2F15": rule1, "config": config_rule1},
}



def output_VID_Rule(var_data):
  rule = ""
  
  for v in var_list:
    if var_data.get(v) is not None:
      rule += '''
SET;
VID=%s
CONV=%s
END;
''' % (str(v), var_data[v])
  return rule

def output_S2F15_Rule(var_data):
  rule = ""
  
  for v in var_list:
    if var_data.get(v) is not None:
      rule += '''
SET;
STREAM=2
FUNCTION=15
POSITION=1,2,%d,2
CONV=%s
END;
''' % (var_list.index(v)+1, var_data[v])
  return rule

def output_S2F14_Rule(var_data):
  rule = ""
  
  for v in var_list:
    if var_data.get(v) is not None:
      rule += '''
SET;
STREAM=2
FUNCTION=14
POSITION=1,%d
CONV=%s
END;
''' % (var_list.index(v)+1, var_data[v])
  return rule


def output_S2F13(is_ascii):
  sml = '''S2F13 W
<L
  <A "EQPID">
  <L'''

  for v in var_list:
    if is_ascii:
      sml += '''
    <A "%s">''' % (v)
    else:
      sml += '''
    <U4 %d>''' % (v)

  sml += '''
  >
> .'''

  return sml

def output_S2F15(sf_name, var_data, is_ascii):
  # var_data = { vid: data }
  sml = '''%s W
<L
  <A "EQPID">
  <L''' % sf_name

  for v in var_list:
    if var_data.get(v) is not None:
      if is_ascii:
        sml += '''
    <L
      <A "%d">
      <A "%s">
    >''' % (v, var_data[v])
      else:
        sml += '''
    <L
      <U4 %d>
      <%s %s>
    >''' % (v, var_data_list[v]["type"],
            '"' + var_data[v] + '"' if var_data_list[v]["type"] == "A" else var_data[v])

  sml += '''
  >
> .'''

  return sml

def main():
  print output_S2F13(False)

  for i in range(len(rule1)):
    var_data = {}
    for v in var_data_list:
      v_type = var_data_list[v]["type"]
      rule = var_data_list[v]["S2F15"][i]
      var_data[v] = rule.replace("#UP", str(var_limits[v_type]["UP"])).replace("#DOWN", str(var_limits[v_type]["DOWN"]))
    
    print
    print output_S2F15("S2F15_"+str(i+1), var_data, False)

  var_data = {}
  for v in var_data_list:
    v_type = var_data_list[v]["type"]
    rule = ",".join(var_data_list[v]["config"])
    var_data[v] = rule.replace("#UP", str(var_limits[v_type]["UP"])).replace("#DOWN", str(var_limits[v_type]["DOWN"]))
    
  print
  print "######### config[S2F15] #########"
  print output_S2F15_Rule(var_data)
  print
  print "######### config[S2F14] #########"
  print output_S2F14_Rule(var_data)
  print
  print "######### config[VID] #########"
  print output_VID_Rule(var_data)


if __name__ == "__main__":
  main()