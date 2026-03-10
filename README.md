# r3000
MIPS r3000 & GTE single-step tests.

# sh4 JSON tests
If you've used TomHarte-style JSON tests before, this may be familiar to you.

This repository hosts a bunch of tests for a MIPS R3000 as found in the Sony PlayStation. It was generated using Ares' CPU interpreter, using the fork at https://github.com/SingleStepTests/ares_r3000_ssts.

This only tests the basic functionality of the valid MIPS encodings. Enough to get you through the BIOS and into some games, at least.

You must run transcode_json.py after pulling the tests. This will translate the .json.bin format into .json format to easily work with. If you wish to use the binary representation, the .py file should document it fairly clearly.

Each .JSON file represents a valid encoding for an instruction, plus the PR and SZ bits for this.

Each tests has a list with 500 entries that look like this (this is from 0110nnnnmmmm0000_sz0_pr0.json):

```json
{
  "initial": {
    "R": [
      2439438834,
      656238375,
      2611285952,
      3165037489,
      313840832,
      3526939960,
      3718168823,
      3328684589,
      305185032,
      3127902481,
      1817167985,
      3216387433,
      1988875386,
      1749641138,
      3172172666,
      2476819955
    ],
    "R_": [
      2851628040,
      395136730,
      3792091456,
      1414502100,
      97644723,
      2019566466,
      1445018913,
      3354311430
    ],
    "FP0": [
      3626478839,
      1399497680,
      869405182,
      3320426796,
      4159368018,
      332055238,
      4178119026,
      4280931894,
      2562944062,
      212597369,
      2244073807,
      2389929555,
      1752903741,
      1416388558,
      920312990,
      3466410236
    ],
    "FP1": [
      62002743,
      429963413,
      1927115332,
      3242538682,
      3927151297,
      2886081679,
      2904868278,
      2937712015,
      1318836025,
      1993771878,
      17043105,
      1338537593,
      3933907350,
      463175977,
      1568874634,
      4099511153
    ],
    "PC": 1384424920,
    "GBR": 689058560,
    "SR": 1073741826,
    "SSR": 632069744,
    "SPC": 767683386,
    "VBR": 497142336,
    "SGR": 1618002282,
    "DBR": 2131555375,
    "MACL": 929931190,
    "MACH": 3550844333,
    "PR": 3017805154,
    "FPSCR": 262147
  },
  "final": {
    "R": [
      2439438834,
      2,
      2611285952,
      3165037489,
      313840832,
      3526939960,
      3718168823,
      3328684589,
      305185032,
      3127902481,
      1817167985,
      3216387433,
      1988875386,
      1749641138,
      3172172666,
      2476819955
    ],
    "R_": [
      2851628040,
      395136730,
      3792091456,
      1414502100,
      97644723,
      2019566466,
      1445018913,
      3354311430
    ],
    "FP0": [
      3626478839,
      1399497680,
      869405182,
      3320426796,
      4159368018,
      332055238,
      4178119026,
      4280931894,
      2562944062,
      212597369,
      2244073807,
      2389929555,
      1752903741,
      1416388558,
      920312990,
      3466410236
    ],
    "FP1": [
      62002743,
      429963413,
      1927115332,
      3242538682,
      3927151297,
      2886081679,
      2904868278,
      2937712015,
      1318836025,
      1993771878,
      17043105,
      1338537593,
      3933907350,
      463175977,
      1568874634,
      4099511153
    ],
    "PC": 1384424928,
    "GBR": 689058560,
    "SR": 1073741826,
    "SSR": 632069744,
    "SPC": 767683386,
    "VBR": 497142336,
    "SGR": 1618002282,
    "DBR": 2131555375,
    "MACL": 929931190,
    "MACH": 3550844333,
    "PR": 3017805154,
    "FPSCR": 262147
  },
  "cycles": [
    {
      "actions": 4,
      "fetch_addr": 1384424920,
      "fetch_val": 9
    },
    {
      "actions": 4,
      "fetch_addr": 1384424922,
      "fetch_val": 25008
    },
    {
      "actions": 5,
      "fetch_addr": 1384424924,
      "fetch_val": 12572,
      "read_addr": 3216387433,
      "read_val": 1
    },
    {
      "actions": 4,
      "fetch_addr": 1384424926,
      "fetch_val": 9
    }
  ],
  "opcodes": [
    9,
    25008,
    12572,
    9,
    12844
  ]
}
```

At the high level, there are the following entries:

'initial' and 'final', which represent processor state before and after the tests, and include many of the registers.

'opcodes', which lists the opcodes as they are fetched from memory (more on this lower, it works a little differently than you'd expect.)

And finally, 'cycles', which lists what happened on each cycle. Except fetch_val appears bugged right now. The 'actions' in each cycle is a bitmask, where bit 1 is read, 2 is write, and 4 is instruction fetch.

Note that this assumes no real pipeline, though delay slots are tested for and supported.

The opcodes in any give test go like this:

XOR R3, R2, R1      <-- start off with a NOP
opcode              <-- run our opcode
XOR R6, R5, R4      <-- this will be in a delay slot, thus allowing detection of whether or not a delay slot is executed after an instruction
XOR R9, R8, R7      <-- this allows the last instruction to not be a delay-slot
XOR R12, R11, R10   <-- if a branch is taken or PC goes haywire this will be the last instruction executed 
provided to anything not in the normal instruction flow

The first 4 are provided for the first 4 instruction fetches, starting at PC; the last one is provided for any instruction fetch anywhere else in memory.

To run the test, set your CPU up by the initial state, run 4 cycles, and compare to the end state. Also compare what happens each instruction/cycle, to what your emulator does.

Pseudocode for making use of these:

```
read_instruction(test, addr) {
    if addr != test.cycles[test.cpu.cycle_number].fetch_addr]): alert issue
    num = (addr - test.base_addr) / 2;
    if ((num >= 0) && (num <= 3)): return test.opcodes[num];
    return test.opcodes[4];
}

read_ram(test, addr) {
    if test.read_addr != addr: alert issue
    test.did_read = true;
    return test.read_val
}

write_ram(test, addr, val) {
    if test.write_addr != addr: alert issue
    if test.write_val != val: alert issue
    test.did_write = true
}

do_test(test, cpu) {
    copy test initial state to CPU;
    cpu.ins_fetch = &read_instruction;
    cpu.read_mem = &read_ram;
    cpu.write_mem = &write_ram;
    
    test.base_addr = test.initial.PC;
    test.did_write = test.did_read = false;
    
    cpu.run_cycles(4);
    
    if (!compare_cpu_state_to_final(cpu, test.final)): raise alert;
    if (!check_reads_and_writes(test, test.cycles)): raise alert;
}

// Test that any reads or writes that were supposed to happen, did happen
check_reads_and_writes(test, cycles) {
    if (test.did_write != cycles_have_a_write(cycles)): raise alert;
    if (test.did_read != cycles_have_a_read(cycles)): raise alert;
}

```

Disclaimers:

* The tests DO NOT include tests for MACL, MACH, or PREF! (See above. They don't work with current test format)
* The tests do not properly restrict reads and writes to byte-alignment, other than instructions.
* The tests treat RAM as a 32-bit flat space with no memory-mapped registers.
* The tests may have bugs, this is an in-development release v0.1
* This was developed by hacking parts of my emulator (jsmooch-emus) into Reicast. There may be issues with the tests we don't know yet.
* Toggling RB causes the first 8 registers in R and R_ to actually swap, instead of updating some internal reference to them. That's how the 4 emulators I know of do it, so the test does too.

Also. If you're using these for SH2, the following tests have incompatibilities:
```
0000000000101011   RTE
0100mmmm00000111   LDC.L @Rm+, SR
0100mmmm00001110   LDC Rm, SR
11000011iiiiiiii   TRAPA #imm
```

I hope you find it useful!
