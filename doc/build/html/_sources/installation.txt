===============
1. Installation
===============

1.1 Prerequisite
================
(1) Python 2.7.6
(2) Python module: numpy
(3) Pyhton module: pandas
(4) Python module: sklearn
(5) Python module: scipy
(6) Python module: kdb
(7) Cython
(8) KDB

1.2 VSCHON package intallation
==============================
1. Create VSCHON directory in /path/to/desired/VSCHON
2. Copy the entire VA_PYTHON directory to /path/to/VSCHON/VA_PYTHON
3. Copy the entire VD_KDB directory to /path/to/VSHON/VD_KDB
4. Put following lines in .bashrc

::

   export VSCHON=/path/to/VSCHON
   export PYTHONPATH=$PYTHONPATH:$VSCHON/VA_PYTHON
   export PYTHONPATH=$PYTHONPATH:$VSCHON/VD_KDB

1.3 VSCHON DATA intallation
===========================
DATA directory is the root directory of all databases. Currently, there are two complete databases in DATA:

1. forex_taqDB: stores the best bid/ask change of 15 major currency pairs from 2009 May to 2013 July.
2. Edgar: stores the form10Q/K(Quarterly and annual report to SEC)  of all US stocks from 1993 to 2013.
3. All the databases are managed by the "datamanage" submodule in VA_PYTHON package. To properly use the database, please:

 (1) Create Data directory in /path/to/Data

 (2) Add following line to .bashrc

 ::    

  export DATA=/path/to/Data

 (3) Copy the forex_taqDB and Edgar to DATA.


