

# Return {} or the first json object of a certain key/value
# j is an array of json
# key is the key you want filter
# value is the value
def retFirstVal(j, key, value):
    r = [x for x in j if x[key] == value]
    r = r[0] if len(r) else {}
    return r