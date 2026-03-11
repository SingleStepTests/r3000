# r3000
MIPS r3000 & GTE single-step tests.

# sh4 JSON tests
If you've used TomHarte-style JSON tests before, this may be familiar to you.

This repository hosts a bunch of tests for a MIPS R3000 as found in the Sony PlayStation. It was generated using Ares' CPU interpreter, using the fork at https://github.com/SingleStepTests/ares_r3000_ssts.

This only tests the basic functionality of the valid MIPS encodings. Enough to get you through the BIOS and into some games, at least.

To get .json files, you must run transcode_json.py after pulling the tests. This will translate the .json.bin format into .json format to easily work with. If you wish to use the binary representation, the .py file should document it fairly clearly.

Each .JSON file represents valid encodings for the given instruction.

Each test has a list with 1000 entries that look like this (this is from ADD.json):

```json
  {
  "name": "ADD $20e",
  "opcode": 1908128,
  "opcode_addr": 3353997064,
  "initial": {
    "R": [
      0,
      1387367053,
      3534999571,
      3781668812,
      2934720738,
      1121915977,
      3569425707,
      662065234,
      4184471979,
      3918554708,
      2182088688,
      923870132,
      4283467195,
      3908572534,
      2205621898,
      995027946,
      1493729718,
      336499120,
      2197668752,
      2324290861,
      2037832853,
      2174880252,
      1399639508,
      2561814256,
      2742058904,
      2291920362,
      3850080350,
      4074045800,
      3654344806,
      2462968976,
      3910498537,
      1165704274
    ],
    "hi": 2512090091,
    "lo": 1470262143,
    "EPC": 880480564,
    "PC": 2302685708,
    "delay": {
      "load": {
        "slot": false,
        "take": false,
        "target": 0
      },
      "branch": {
        "target": 26,
        "val": 55491267
      }
    }
  },
  "final": {
    "R": [
      0,
      1387367053,
      3534999571,
      3781668812,
      2934720738,
      1121915977,
      3569425707,
      662065234,
      4184471979,
      3918554708,
      2182088688,
      923870132,
      4283467195,
      3908572534,
      2205621898,
      995027946,
      1493729718,
      336499120,
      2197668752,
      2324290861,
      2037832853,
      2174880252,
      1399639508,
      2561814256,
      2742058904,
      2291920362,
      55491267,
      4074045800,
      3654344806,
      2462968976,
      3910498537,
      1165704274
    ],
    "hi": 2512090091,
    "lo": 1470262143,
    "EPC": 880480564,
    "PC": 2302685712,
    "delay": {
      "load": {
        "slot": true,
        "take": false,
        "target": 2302609848
      },
      "branch": {
        "target": -1,
        "val": 0
      }
    }
  },
  "cycles": [
    {
      "actions": 4,
      "sz": 4,
      "addr": 2302685708,
      "val": 296662506
    }
  ]
}
```

At the high level, there are the following entries:

'name', a human-readable name for the test.

'initial' and 'final,' which represent processor state before and after the tests, and include many of the registers. This also includes the branch delay and load delay statuses. These must be implemented to properly emulate the processor, so they are included. delay.load.slot represents whether the next instruction it is in a delay slot. delay.load.take, if the branch is taken. delay.load.target, the target of the branch.

For register delay slots, delay.load.target is the register that will be updated, where -1 indicates "no load delay." Val is the value to assign to it.

'opcode' and 'opcode_addr', which list the opcode being tested and its address.

And finally, 'cycles', which lists what happened on each cycle.

To run the test, set your CPU up by the initial state, run 4 cycles, and compare to the end state. Also compare what happens each instruction/cycle, to what your emulator does.

!!!PLEASE NOTE!!! READ THE CAVETAS! 

Caveats:

* These tests do not include coprocessor tests. I may include a GTE set in the near future.
* The tests do not properly restrict reads and writes to byte-alignment, other than the first instruction. Exceptions have been DISABLED for these tests, so there are no address exceptions.
* The tests treat all of RAM as a 32-bit flat space with no MMIO, even that internal to the R3000. However, instructions are only generated in the address range 0x00000000-0xEFFFFFFF.
* On a real R3000, when the core requests a 8-bit or 16-bit save to memory, it sends the whole 32-bit value of the register to memory. It's up to the bus to only use the portion of it that it wishes. This is why instructions like SB that have 1-byte saves, include a full 32-bit value! These tests also provide a full 32-bit value for all loads.

I hope you find it useful!
