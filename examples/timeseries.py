"""
Example usage of iress.IressDataClient to fetch weekly close
prices of BHP.

Outputs BHP's weekly close price for 2008 as CSV.

"""

import operator
from iress import IressDataClient, DfsTimeSeries

if __name__ == '__main__':
    idc = IressDataClient()
    idc.connect()

    # Fetch timeseries data for BHP during 2008.
    timeseries = idc.execute(DfsTimeSeries.constants.dfsDataTimeSeries, dict(
        Security='BHP',
        Exchange='ASX',
        Start='01/01/2008',
        End='31/12/2008',
        Frequency=DfsTimeSeries.constants.Weekly,
        Adjusted=True,
    ))
    
    # Output date and close price as csv.
    print 'Date,Close'
    for x in sorted(timeseries, key=operator.itemgetter('Date')):
        print '%s,%f' % (x['Date'].Format('%Y-%m-%d'), x['ClosePrice']/100.0)
