from flask import current_app

def key_com(key,x,n):
    '''
    key combinations
    '''
    seen = []
    i = 0
    x = x
    li = 0
    while True:
        if li+x+1 >= len(key):
            li = 0
            x += 1
        
        k = key[li:li+x]
        li +=1
        if k not in seen:
            seen.append(k)
            yield k
            if len(seen) > n:
                break

def create_map(key):
    numbers = [chr(x) for x in range(48,58)]
    letters = [chr(x) for x in range(97,123)] + ["_"]+[" "]
    characters = numbers + letters
    key_combinations = key_com(key,3,len(characters))
    encode_map = { }
    decode_map = { }
    
    for char,rep in zip(characters, key_combinations):
        encode_map[char] = rep
        decode_map[rep] = char
        
    return encode_map, decode_map

def custom_encode(msg):
    msg = msg.lower().strip()
    char_map = current_app.config["ENDOCE_MAP"]
    out = ""
    for x in msg:
        if x == ":":
            out += "-"
        else:
            out += char_map[x]
    return out

def custom_decode(msg):
    decode_map = current_app.config["DECODE_MAP"]
    count = current_app.config["ENCODE_COUNT"]
    sections = [x for x in msg.strip().split("-") if x]
    out = ""
    for x in sections:
        if len(x) % count == 0:
            c = len(x) // count
            i = 0
            for k in range(1,c+1):
                rep = x[i:i+count]
                i = count * k
                if rep not in decode_map:
                    return False
                out += decode_map[rep]
        out += ":"
    
    return out[:-1]
