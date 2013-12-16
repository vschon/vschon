=============================
2. Overview of VSCHON Package
=============================

There are three main components that consists VSCHON:

- **VSCHON ANALYSIS** (VA_PYTHON, or va): It is the major component for model analysis,
  trading stratrgy backtesting.Written in python and Cython. To use::

   >>>import VA_PYTHON

  or::

   >>>import VA_PYTHON as va
    
- **VSCHON DATABASE Management** (VD_KDB, or vd): This component contains the database manager for each database.
  It also contains the python API to communicate with KDB database. To use::

   >>>import VD_KDB

  or::

   >>>import VD_KDB as vd
    
- **VSCHON DATA**: All databases are physically stored in DATA.


