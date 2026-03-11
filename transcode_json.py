#!/usr/bin/python3
import os
import glob
import json
from struct import unpack_from
from typing import Dict, Any

R3000_JSON_PATH = os.path.expanduser('~') + '/dev/r3000/v1/'

def load_state(buf, ptr) -> (int, Any):
    start_ptr = ptr
    state = {'R' : []}
    for i in range (0, 32):
        state['R'].append(unpack_from('I', buf, ptr)[0])
        ptr += 4
    state['hi'], state['lo'], state['EPC'], state['PC'] = unpack_from('IIII', buf, ptr)
    if state['R'][0] != 0:
        print('WARN R0 != 0!')
    ptr += 16

    #load target, slot, take
    ltarget, lslot, ltake = unpack_from('III', buf, ptr)
    ptr += 12
    lslot = True if lslot != 0 else False
    ltake = True if ltake != 0 else False

    #branch i32 target, u32 val
    btarget, bval = unpack_from('iI', buf, ptr)
    ptr += 8
    state['delay'] = {'load': {'slot': lslot, 'take': ltake, 'target': ltarget},
                      'branch': {'target': btarget, 'val': bval} }

    full_sz = ptr - start_ptr
    return full_sz, state

def load_cycles(buf, ptr) -> (int, Dict):
    start_ptr = ptr
    num_cycles = unpack_from('I', buf, ptr)[0]
    ptr += 4
    cycles = []

    for i in range(0, num_cycles):
        val, actions, addr, sz = unpack_from('=qIqI', buf, ptr)
        ptr += 24
        cycle = {'actions': actions, 'sz': sz, 'addr': addr, 'val': val}
        cycles.append(cycle)

    full_sz = ptr - start_ptr
    return full_sz, cycles

def load_opcodes(buf, ptr):
    full_sz = unpack_from('i', buf, ptr)[0]
    opcodes = []
    ptr += 8
    values = unpack_from('IIIII', buf, ptr)
    return full_sz, list(values)

def decode_test(buf, ptr) -> (int, Dict):
    test = {}
    start_ptr = ptr

    name = unpack_from('51p', buf, ptr)[0]
    test['name'] = name.decode('ascii')
    ptr += 51
    test['opcode'], test['opcode_addr'] = unpack_from('II', buf, ptr)
    ptr += 8
    sz, test['initial'] = load_state(buf, ptr)
    ptr += sz
    sz, test['final'] = load_state(buf, ptr)
    ptr += sz
    sz, test['cycles'] = load_cycles(buf, ptr)
    ptr += sz

    full_sz = ptr - start_ptr

    return full_sz, test



def decode_file(infilename, outfilename):
    with open(infilename, 'rb') as infile:
        content = infile.read()
    ptr = 0
    tests = []
    NUMTESTS = unpack_from('i', content, ptr)[0]
    ptr += 4
    for i in range(0, NUMTESTS):
        sz, test = decode_test(content, ptr)
        ptr += sz
        tests.append(test)
    if os.path.exists(outfilename):
        os.unlink(outfilename)
    with open(outfilename, 'w') as outfile:
        outfile.write(json.dumps(tests, indent=2))

def do_path(where):
    print("Doing path...", where)
    fs = glob.glob(where + '**.json.bin')
    for fname in fs:
        decode_file(fname, fname[:-4])

def main():
    do_path(R3000_JSON_PATH)

if __name__ == '__main__':
    main()
