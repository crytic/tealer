# Teal Analyzer
Teal Analyzer is a static analyzer for Teal code. It parses the Teal program, and builds its CFG. The analyzer comes with a set of vulnerabilities detectors and printers allowing to quickly review the contracts.

- [Features](#features)
- [How to install](#how-to-install)
- [How to run](#how-to-run)

## Features
### Detectors
- Detect paths with a missing RekeyTo check (group transaction) 
- Detect paths with a missing GroupSize check (group transaction) 

All the detectors are run by default

### Printers 
- Print CFG (`--print-cfg`)
- Print paths that can delete the application (`--print-delete`)
- Print paths that can update the application (`--print-update`)

Printers output [`dot`](https://graphviz.org/) files.
Use `xdot` to open the files  (`sudo apt install xdot`).

## How to install
Run
```
python3 setup.py develop
```

This project is at a beta stage, we recommend to install the tool in a virtualenv

## How to run
```
teal-analyzer code.teal
```

### Example:
The following show the CFG from [algorand/smart-contracts](https://github.com/algorand/smart-contracts.git).
```
git clone https://github.com/algorand/smart-contracts.git
cd smart-contracts
teal-analyzer ./devrel/permission-less-voting/vote_opt_out.teal --print-cfg
```

<img src="./examples/vote_opt_out.png" alt="Example" width="500"/>

