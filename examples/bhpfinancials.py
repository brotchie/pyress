"""
Example usage of iress.IressDataClient that fetches all financials
for BHP during 2008.

"""

import pprint
from iress import IressDataClient, DfsSec

if __name__ == '__main__':
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
