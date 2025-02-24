# gsfpy_USM_Implementation
![Python Package](https://github.com/UKHO/gsfpy/workflows/Python%20Package/badge.svg) ![PyPI - Downloads](https://img.shields.io/pypi/dm/gsfpy)

This repository is originally created by UKHO to wrap the GSF C-library written and maintained by Leidos. This fork of the repository is intended to be further developed to suite the purposes of hydrographic research at the University of Southern Mississippi.

Please see below for the original readme from UKHO

# gsfpy - Generic Sensor Format for Python



Python wrapper for the C implementation of the Generic Sensor Format library.

- Free software: MIT license
- __Notes on licensing__: The bundled `gsfpy3_0x/libgsf/libgsf03_0x.so` binaries are covered by the [LGPL v2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html) license. Copies of this license are included in the project at `gsfpy3_0x/libgsf/libgsf_LICENSE.md`. The top-level MIT licensing of the  overall `gsfpy` project is not affected by this. However, as required by the libgsf license, the libgsf shared object libraries used by the `gsfpy3_0x` packages at runtime may be replaced with a different version by setting the `GSFPY3_08_LIBGSF_PATH` and/or `GSFPY3_09_LIBGSF_PATH` environment variables to the absolute file path of the new library.

## Namespaces and supported GSF versions
The `gsfpy` package provides three namespaces: `gsfpy`, `gsfpy3_08` and `gsfpy3_09`.

The default version of GSF supported is `3.08`. Top level package functionality for `3.08` can be used either via `import gsfpy` (without setting the `DEFAULT_GSF_VERSION` environment variable - see below) or `import gsfpy3_08`. Note that `import gsfpy` will also work for versions 3.06 and 3.07 of GSF as well (older versions have not been tested).

If you are using GSF v3.09, there are two options:
* Set the `DEFAULT_GSF_VERSION` environment variable to `"3.09"`, then `import gsfpy`
* Import the 3.09 package directly with `import gsfpy3_09`


## Features

- The `gsfpy(3_0x).bindings` modules provide wrappers for all GSFlib functions, including I/O, utility and info functions.
  Minor exceptions are noted in the sections below.

- For added convenience the gsfpy top level package provides the following higher level abstractions:
  - `open_gsf()`
  - `GsfFile` (class)
  - `GsfFile.read()`
  - `GsfFile.get_number_records()`
  - `GsfFile.seek()`
  - `GsfFile.write()`
  - `GsfFile.close()`

## Install using `pip`

#### From PyPI
```shell script
pip install gsfpy
```
#### From GitHub (SSH)
```shell script
pip install git+ssh://git@github.com/UKHO/gsfpy.git@master
```
#### From GitHub (HTTPS)
```shell script
pip install git+https://github.com/UKHO/gsfpy.git@master
```

## Examples of usage

### Open/close/read from a GSF file (GSF v3.08)

```python
from ctypes import string_at

from gsfpy3_08 import open_gsf
from gsfpy3_08.enums import RecordType

with open_gsf("path/to/file.gsf") as gsf_file:
    # Note - file is closed automatically upon exiting 'with' block
    _, record = gsf_file.read(RecordType.GSF_RECORD_COMMENT)

    # Note use of ctypes.string_at() to access POINTER(c_char) contents of
    # c_gsfComment.comment field.
    print(string_at(record.comment.comment))
```

### Write to a GSF file (GSF v3.09)

```python
from ctypes import c_int, create_string_buffer

from gsfpy3_09 import open_gsf
from gsfpy3_09.enums import FileMode, RecordType
from gsfpy3_09.gsfRecords import c_gsfRecords

comment = b"My comment"

# Initialize the contents of the record that will be written.
# Note use of ctypes.create_string_buffer() to set POINTER(c_char) contents.
record = c_gsfRecords()
record.comment.comment_time.tvsec = c_int(1000)
record.comment.comment_length = c_int(len(comment))
record.comment.comment = create_string_buffer(comment)

with open_gsf("path/to/file.gsf", mode=FileMode.GSF_CREATE) as gsf_file:
    gsf_file.write(record, RecordType.GSF_RECORD_COMMENT)
```

### Copy GSF records (GSF v3.08 as default)

```python
from ctypes import byref, c_int, pointer

from gsfpy import *


# This example uses the bindings module to illustrate use of the lower level functions
file_handle = c_int(0)
data_id = gsfDataID.c_gsfDataID()
source_records = gsfRecords.c_gsfRecords()
target_records = gsfRecords.c_gsfRecords()

ret_val_open = bindings.gsfOpen(
    b"path/to/file.gsf", enums.FileMode.GSF_READONLY, byref(file_handle)
)

# Note use of ctypes.byref() as a shorthand way of passing POINTER parameters to
# the underlying foreign function call. ctypes.pointer() may also be used.
bytes_read = gsfpy.bindings.gsfRead(
    file_handle,
    enums.RecordType.GSF_RECORD_COMMENT,
    byref(data_id),
    byref(source_records),
)

# Note use of pointer() rather than byref() when passing parameters to
# gsfCopyRecords(). Implementation of this function is in Python as calling
# the native underlying function causes memory ownership clashes. byref()
# is only suitable for passing parameters to foreign function calls (see
# ctypes docs).
ret_val_cpy = bindings.gsfCopyRecords(
    pointer(target_records), pointer(source_records)
)
ret_val_close = bindings.gsfClose(file_handle)
```

### Troubleshoot

```python
from gsfpy3_09.bindings import gsfIntError, gsfStringError

# The gsfIntError() and gsfStringError() functions are useful for
# diagnostics. They return an error code and corresponding error
# message, respectively.
retValIntError = gsfIntError()
retValStringError = gsfStringError()
print(retValIntError, retValStringError)
```

## Notes on implementation

### gsfPrintError()

The `gsfPrintError()` method of GSFlib is not implemented as there is no
`FILE*` equivalent in Python. Use `gsfStringError()` instead - this will
give the same error message, which can then be written to file as
required.

### gsfCopyRecords() and gsfFree()

`gsfFree()` the sibling method to `gsfCopyRecord()` in GSFlib, used to
deallocate memory assigned by the library but managed by the calling
application, is not required by gsfpy as memory allocation and
deallocation is handled by ctypes. `gsfFree()` is therefore omitted from
the package.

### gsf_register_progress_callback()

Implementation of the GSFlib function
`gsf_register_progress_callback()` is not applicable for gsfpy as the
DISPLAY_SPINNER macro was not defined during compilation. It is
therefore omitted from the package.

## Generic Sensor Format Documentation

Generic Sensor Format specification: see e.g.
<https://github.com/schwehr/generic-sensor-format/blob/master/doc/GSF_lib_03-06.pdf>

Generic Sensor Format C library v3.06 specification: see e.g.
<https://github.com/schwehr/generic-sensor-format/blob/master/doc/GSF_spec_03-06.pdf>

More recent versions of these documents can be downloaded from the
[Leidos](https://www.leidos.com/products/ocean-marine) website.

## Dev Setup

[Ensure Poetry is installed before proceeding](https://python-poetry.org/docs/#installation)

### Poetry (Recommended)
By default Poetry will create it's own virtual environment using your system's Python. [This feature can be disabled.](https://python-poetry.org/docs/faq/#i-dont-want-poetry-to-manage-my-virtual-environments-can-i-disable-it)

```shell script
git clone git@github.com:UKHO/gsfpy.git
cd gsfpy
poetry install
```

### Pyenv

A good choice if you want to run a version of Python different than available through your system's package manager

```shell script
git clone git@github.com:UKHO/gsfpy.git
cd gsfpy
pyenv install 3.8.3
pyenv virtualenv 3.8.3 gsfpy
pyenv local gsfpy
poetry install
```

## Run Tests

```shell script
make test
```

## Run Checks

```shell script
make lint
```

## Notes on Security

Some known concerns relating to the underlying GSFlib C library are
documented at <https://github.com/dwcaress/MB-System/issues/368> and
<https://github.com/schwehr/generic-sensor-format/issues>. Note that
gsfpy simply wraps GSFlib and does not purport to stop or mitigate these
potential vulnerabilities. It is left to the authors of applications
calling gsfpy to assess these risks and mitigate where deemed necessary.

GSF data processed using gsfpy should be sourced from reliable providers
and checked for integrity where possible.

Please also refer to the LICENSE file for the terms of use of gsfpy.

## Credits

`libgsf03-08.so` was built from the
[Leidos](https://www.leidos.com/products/ocean-marine) C code using the
Makefile in [UKHO/libgsf](https://github.com/UKHO/libgsf)

This package was created with
[Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the
[UKHO/cookiecutter-pypackage](https://github.com/UKHO/cookiecutter-pypackage)
project template.

## Related Projects

Also see [schwehr/generic-sensor-format](https://github.com/schwehr/generic-sensor-format/)
