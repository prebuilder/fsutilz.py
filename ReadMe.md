fsutilz.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
[![GitLab Build Status](https://gitlab.com/KOLANICH/fsutilz.py/badges/master/pipeline.svg)](https://gitlab.com/KOLANICH/fsutilz.py/pipelines/master/latest)
![GitLab Coverage](https://gitlab.com/KOLANICH/fsutilz.py/badges/master/coverage.svg)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/fsutilz.py.svg)](https://libraries.io/github/KOLANICH/fsutilz.py)

Just a set of functions and classes fixing some problems in shutil API and features. Not targeted to mimic it completely. Not targeted to be well documented. Currently used only by my packages.


Requirements
------------
* [`Python >=3.4`](https://www.python.org/downloads/). [`Python 2` is dead, stop raping its corpse.](https://python3statement.org/) Use `2to3` with manual postprocessing to migrate incompatible code to `3`. It shouldn't take so much time. For unit-testing you need Python 3.6+ or PyPy3 because their `dict` is ordered and deterministic. Python 3 is also semi-dead, 3.7 is the last minor release in 3.
