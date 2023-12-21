# Tealer

Tealer is a static analyzer for [Teal](https://developer.algorand.org/docs/features/asc1/) code.
It parses the Teal program, and builds its CFG. The analyzer comes with a set of vulnerabilities detectors and printers allowing to quickly review the contracts.
In addition, tealer allows for custom path discovery through [regular expression](#regular-expression), and can be configured to follow the [group information](#group-configuration) of the application.

- [Usage](#Usage)
  - [Detectors](#detectors): Vulnerabilities detectors
  - [Printers](#printers): Visual information
  - [Regular expression](#regular-expression): Regular expression engine
- [How to install](#how-to-install)
- [Group configuration](#group-configuration)

## Usage

To detect vulnerabilities

```bash
tealer detect --contracts file.teal
```

To run a printer

```bash
tealer print <printer_name> --contracts file.teal
```

To run the regular expression engine

```bash
tealer regex <regex_file.txt> --contracts file.teal
```


For additional configuration, see the [Usage](https://github.com/crytic/tealer/wiki/Usage) documentation.

### Detectors

| Num | Detector                | What it detects                                                                                                                                     | Applies To          | Impact       | Confidence |
|-----|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|--------------|------------|
| 1   | `is-deletable`          | [Deletable Applications](https://github.com/crytic/tealer/wiki/Detector-Documentation#deletable-application)                                        | Stateful            | High         | High       |
| 2   | `is-updatable`          | [Upgradable Applications](https://github.com/crytic/tealer/wiki/Detector-Documentation#upgradable-application)                                      | Stateful            | High         | High       |
| 3   | `unprotected-deletable` | [Unprotected Deletable Applications](https://github.com/crytic/tealer/wiki/Detector-Documentation#unprotected-deletable-application)                | Stateful            | High         | High       |
| 4   | `unprotected-updatable` | [Unprotected Upgradable Applications](https://github.com/crytic/tealer/wiki/Detector-Documentation#unprotected-updatable-application)               | Stateful            | High         | High       |
| 5   | `group-size-check`      | [Usage of absolute indexes without validating GroupSize](https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-groupsize-validation) | Stateless, Stateful | High         | High       |
| 6   | `can-close-account`     | [Missing CloseRemainderTo field Validation](https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-closeremainderto-field-validation) | Stateless           | High         | High       |
| 7   | `can-close-asset`       | [Missing AssetCloseTo Field Validation](https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-assetcloseto-field-validation)         | Stateless           | High         | High       |
| 8   | `missing-fee-check`     | [Missing Fee Field Validation](https://github.com/crytic/tealer/wiki/Detector-Documentation#missing-fee-field-validation)                           | Stateless           | High         | High       |
| 9   | `rekey-to`              | [Rekeyable Logic Signatures](https://github.com/crytic/tealer/wiki/Detector-Documentation#rekeyable-logicsig)                                       | Stateless           | High         | High       |
| 10  | `constant-gtxn`         | [Unoptimized Gtxn](https://github.com/crytic/tealer/wiki/Detector-Documentation#Unoptimized-Gtxn)                                                   | Stateless           | Optimization | High       |
| 11  | `self-access`           | [Unoptimized self access](https://github.com/crytic/tealer/wiki/Detector-Documentation#Unoptimized-self-access)                                     | Stateless           | Optimization | High       |
| 12  | `sender-access`         | [Unoptimized Gtxn](https://github.com/crytic/tealer/wiki/Detector-Documentation#Unoptimized-sender-access)                                          | Stateless           | Optimization | High       |


For more information, see

- The [Detector Documentation](https://github.com/crytic/tealer/wiki/Detector-Documentation) for information on each detector
- The [Detection Selection](https://github.com/crytic/tealer/wiki/Usage#detector-selection) to run only selected detectors. By default, all the detectors are ran.

### Printers

| Num | Printer               | What it prints                                    |
|-----|-----------------------|---------------------------------------------------|
| 1   | `call-graph`          | Export the call graph of contract to a dot file   |
| 2   | `cfg`                 | Export the CFG of entire contract                 |
| 3   | `human-summary`       | Print a human-readable summary of the contract    |
| 4   | `subroutine-cfg`      | Export the CFG of each subroutine                 |
| 5   | `transaction-context` | Output possible values of GroupIndices, GroupSize |


Printers output [`dot`](https://graphviz.org/) files.
Use `xdot` to open the files  (`sudo apt install xdot`).

### Regular expression

Tealer can detect if there is a path between a given label and a set of instruction using the `regex` subcommand: `tealer regex regex.txt --contracts file.teal`.

The Regular expression file must be on the form:
```txt
label =>
  ins1
  ins2
```

If there is a match, tealer will generate a DOT file with the graph.

For an example, run `tealer regex tests/regex/regex.txt --contract tests/regex/vote_approval.teal`, with:
- [tests/regex/regex.txt](./tests/regex/regex.txt)
- [tests/regex/vote_approval.teal](./tests/regex/vote_approval.teal)

Which will generate `regex_result.dot`.

## How to install

`pip3 install tealer`

### Using Git

```bash
git clone https://github.com/crytic/tealer.git && cd tealer
make dev
```


## Group configuration

To help tealer reasons about applications that are meant to be run in a group of transaction, the user can provide the group information through a configuration file:
- See the [ANS configuration](tests/group_transactions/ans/ans_config.yaml) example
- See [Lightweight group information specification](https://forum.algorand.org/t/lightweight-group-information-specification/9735) discussion.

The file format is still in development, and it is likely to evolve in the future

## License

Tealer is licensed and distributed under the AGPLv3 license. [Contact us](opensource@trailofbits.com) if you're looking for an exception to the terms.
