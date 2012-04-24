IRESS is a market data system developed by IRESS Market Technology Ltd. Their desktop IRESS solution provides real-time and historical data for wide range of equities and derivatives.

The IRESS application exposes a COM automation object model that allows direct access to the data streams that drive the user interface. *pyress* wraps sections of this COM object model in a pythonic interface.

Installation
============

The latest release of pyress is always available on PyPI at http://pypi.python.org/pypi/pyress/.

You can install the latest pyress library release from the command line using pip or easy_install::

    pip install pyress
    easy_install pyress

If you want to use the latest (potentially unstable) code then grab the master
branch from the pyress github repository::

    pip install -I https://github.com/brotchie/pyress/zipball/master


Example
=======

The following example retrieves then displays all financials for BHP during 2008::

    import pprint
    from iress import IressDataClient, DfsSec

    idc = IressDataClient()
    idc.connect()

    financials = idc.execute(DfsSec.constants.dfsDataFinancial, dict(
        Security='BHP',
        Exchange='ASX',
        StartDate='2008-01-01',
        EndDate='2009-01-01',
        ItemList=-1,
        AnnualReport=True,
        QuarterlyReport=True,
        InterimReport=True,
        PreliminaryReport=True,
    ))  
    pprint.pprint(financials)

This example is available as a script at https://raw.github.com/brotchie/pyress/master/examples/bhpfinancials.py.
