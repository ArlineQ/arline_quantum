# Arline Quantum

**Arline Quantum** is an open-source library providing basic functionality for creating and manipulating quantum
circuits. It also contains a list of mock quantum hardware.

## Installation

```console
$ pip3 install arline-quantum
```

Alternatively, Arline Quantum can be installed locally in the editable mode.
Clone Arline Quantum repository, `cd` to the source directory:

```console
$ git clone https://github.com/ArlineQ/arline_quantum.git
$ cd arline_quantum
```

We recommend to install Arline Quantum in the [virtual environment](https://virtualenv.pypa.io/en/latest/).

```console
$ virtualenv venv
$ source venv/bin/activate
```

If `virtualenv` is not installed on your machine, run

```console
$ pip3 install virtualenv
```

Next in order to install the Arline Quantum platform execute:

```console
$ pip3 install .
```

Alternatively, Arline Quantum can be installed in the editable mode:

```console
$ pip3 install -e .
```

## API documentation

API documentation is here [documentation](https://arline-quantum.readthedocs.io/en/latest/).
To generate HTML API documentation, run below command:

```console
$ cd docs/
$ make html
```

## Running tests

To run unit-tests and check installed dependencies:

```console
$ tox
```

## Folder structure

```
arline_quantum
│
├── arline_quantum            # library
│   ├── gate_chain            # gate chain (circuit) class
│   ├── gate_sets             # collection of gate sets for quantum hardware
│   ├── gates                 # collection of quantum gates
│   ├── hardware              # collection of predefined mock hardware devices
│   ├── qasm_parser           # parser of .qasm circuits
│   └── qubit_connectivity    # list of hardware topologies and utils functions
│   
├── docs                      # documentation
│
└── test                      # tests
    ├── gate_chain            # tests for gate chain class
    ├── gates                 # tests for gates
    ├── hardware              # tests for quantum hardware
    ├── qasm_files            # .qasm files for gate_chain test
    └── qubit_connectivity    # tests for qubit connectivity class
```
