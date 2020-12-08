# Tealer
Tealer is a static analyzer for [Teal](https://developer.algorand.org/docs/features/asc1/) code. It parses the Teal program, and builds its CFG. The analyzer comes with a set of vulnerabilities detectors and printers allowing to quickly review the contracts.

- [Features](#features)
- [How to install](#how-to-install)
- [How to run](#how-to-run)

## Features
### Detectors
 Num |   Check   |               What it Detects                |      Type
--- | --- | --- | ---
  1  | canDelete | Detect paths that can delete the application |    Stateful
  2  | canUpdate | Detect paths that can update the application |    Stateful
  3  | groupSize | Detect paths with a missing GroupSize check  | StatefulGroup
  4  |  rekeyTo  |  Detect paths with a missing RekeyTo check   | StatefulGroup


All the detectors are run by default

### Printers
- Print CFG (`--print-cfg`)

Printers output [`dot`](https://graphviz.org/) files.
Use `xdot` to open the files  (`sudo apt install xdot`).

## How to install
Run
```bash
python3 setup.py install
```

We recommend to install the tool in a [virtualenv](https://virtualenvwrapper.readthedocs.io/en/latest/).

## How to run
```bash
tealer code.teal
```

### Example
The following shows the CFG from [algorand/smart-contracts](https://github.com/algorand/smart-contracts.git).
```bash
git clone https://github.com/algorand/smart-contracts.git
cd smart-contracts
tealer ./devrel/permission-less-voting/vote_opt_out.teal --print-cfg
```

<img src="./examples/vote_opt_out.png" alt="Example" width="500"/>

