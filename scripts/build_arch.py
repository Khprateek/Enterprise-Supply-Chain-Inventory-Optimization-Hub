# Architecture documentation builder
import os

DOLLAR = chr(36)
BSLASH = chr(92)

def S(t):
    return t.replace('__D__', DOLLAR).replace('__B__', BSLASH)

def write_doc(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(S(content).strip() + '\n')
    print(f'Wrote {path}')
