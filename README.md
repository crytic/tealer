# Tealer

Tealer is a static analyzer for [Teal](https://developer.algorand.org/docs/features/asc1/) code. It parses the Teal program, and builds its CFG. The analyzer comes with a set of vulnerabilities detectors and printers allowing to quickly review the contracts.

- [Features](#features)
- [How to install](#how-to-install)
- [How to run](#how-to-run)

## Features

### Detectors

 Num |      Check      |                       What it Detects                        |      Type     | Impact | Confidence
--- | --- | --- | --- | --- | ---
  1  |    isDeletable    |         Detect paths that can delete the application         |    Stateful   |  High  |    High
  2  |    isUpdatable    |         Detect paths that can update the application         |    Stateful   |  High  |    High
  3  |     CanUpdate    | Detect paths that can delete the application AND does not validate the transaction sender. |   Stateful   |  High  |    High
  4  |     CanDelete    | Detect paths that can update the application AND does not validate the transaction sender. |   Stateful   |  High  |    High
  5  |     rekeyTo     |          Detect paths with a missing RekeyTo check           | StatefulGroup |  High  |    High
  6  |    groupSize    |         Detect paths with a missing GroupSize check          | StatefulGroup | Medium |    High
  7  | canCloseAccount |      Detect paths that can close out the sender account      |   Stateless   |  High  |    High
  8  |  canCloseAsset  | Detect paths that can close the asset holdings of the sender |   Stateless   |  High  |    High
  9  |     feeCheck    |            Detect paths with a missing Fee check             |   Stateless   |  High  |    High

All the detectors are run by default

### Printers

- Print CFG (`--print-cfg`): Export the CFG of the contract to a dot file.
- `human-summary`: Print a human-readable summary of the contract.
- `function-cfg`: Export the CFG of each subroutine in the contract, works for contracts written in version 4 or greater.
- `call-graph`: Export the call-graph of the contract to a dot file, works for contracts written in version 4 or greater.

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
