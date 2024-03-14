## Installing pyspartn on 32-bit Linux platforms e.g. Raspberry Pi OS 32

When attempting to install `pyspartn` on some 32-bit Linux platforms (e.g. Raspberry Pi OS 32), you may encounter an error with a missing Rust compiler dependency (`rustc`):

```
Building wheels for collected packages: cryptography
  Building wheel for cryptography (PEP 517): started
  Building wheel for cryptography (PEP 517): finished with status 'error'
Failed to build cryptography
```

This is due to an issue with the way the cryptography library is packaged on some 32-bit platforms.

- The pyspartn library depends on the cryptography>=1.39 library to decrypt SPARTN messages.
- On most platforms, pip can install cryptography from a pre-compiled wheel (.whl) installation package.
- However, on some 32-bit Linux platforms (including Raspberry Pi OS 32 Lite or Full) the cryptography library is only available as a source code (`.tar.gz`) file, which means it has to be compiled by pip at installation time. This in turn requires:
    1. Rust compiler support (as some of cryptography is written in the Rust programming language). This is not installed as standard on most platforms. Specifically, it requires Rust compiler (`rustc`) version 1.56 or later.
    1. A handful of additional cryptography build dependencies, including `libssl-dev` and `libffi-dev`.
- At some point in the future, a wheel (`.whl`) installation package may be made available on 32-bit Linux platforms, but until then some additional installation steps are required. You can either:

    A. (OFFICIAL) Install the Rust toolchain and cryptography library dependencies, then install pyspartn:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    sudo apt-get install build-essential libssl-dev libffi-dev python3-dev pkg-config
    python3 -m pip install --upgrade pip
    python3 -m pip install pyspartn
    ```

    **NB:** On a Raspberry Pi 4 running Raspberry Pi OS 32, you may need to chose "Option 2) Custom installation" when installing Rust and substitute `armv7-unknown-linux-gnueabihf` for the default `aarch64-unknown-linux-gnu` host.

    B. (FASTER) Install cryptography from the pre-compiled wheel (`.whl`) files in this subdirectory, having first copied them to your 32-bit Linux platform and verified the sha256 hash against the supplied `sha256.txt`, then install pyspartn:

    ```shell
    shasum -a 256 cryptography-42.0.5-cp312-cp312-linux_armv7l.whl
    python3 -m pip install cryptography-42.0.5-cp312-cp312-linux_armv7l.whl
    python3 -m pip install --upgrade pip
    python3 -m pip install pyspartn
    ```

