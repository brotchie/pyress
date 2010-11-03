"""
Pythonic interface to Iress data objects.

The following example extracts financial data for BHP:

    from client import IressDataClient, DfsSec

    iress = IressDataClient()
    iress.connect()

    print iress.execute(DfsSec.constants.dfsDataFinancial, dict(
        Security='BHP',
        Exchange='ASX',
        StartDate='2000-01-01',
        EndDate='2008-01-01',
        ItemList=-1,
        AnnualReport=True,
        QuarterlyReport=True,
        InterimReport=True,
        PreliminaryReport=True,
    ))   

"""

import time
import logging

from win32com import client

log = logging.getLogger(__name__)

# Generate and import Python modules for the Iress typelibs.
DfsCmd = client.gencache.EnsureModule('{96EB07E1-03D0-11CF-B214-00AA002F2ED9}', 0, 12, 5007)
DfsPrice = client.gencache.EnsureModule('{DF120F00-A275-11D1-A122-0000F82508F6}', 0, 12, 5005)
DfsSec = client.gencache.EnsureModule('{AF802C80-B975-11D1-A138-0000F82508F6}', 0, 12, 5004)
DfsIndicate = client.gencache.EnsureModule('{9339DB61-1602-11D2-8FC4-0000F824C8AA}', 0, 12, 5003)
DfsTimeSeries = client.gencache.EnsureModule('{4832E620-C2AA-11D1-A143-0000F82508F6}', 0, 12, 5002)

# Default timeout when fetching data from Iress.
DEFAULT_DATA_TIMEOUT = 15

# Number of seconds to wait between polling data object's state.
REQUEST_POLL_INTERVAL = 0.2

class IressError(StandardError):
    pass

class IressDataClient(object):
    """
    Pythonic interface to the Iress data objects automation
    interface.

    """

    def __init__(self):
        self._iress = None

    def connect(self):
        """
        Connects to the running Iress instance.

        """

        self._iress = client.Dispatch('Iress.Application')

    def execute(self, name, params):
        """
        Executes a data object query. Name should be the data object
        type normally passed to CreateOb and params is a dictionary
        of request parameters.

        """

        assert self._iress is not None, 'Not connected to Iress instance.'

        log.debug('Executing query %s with parameters %r.', name, params)

        # Create and execute a data request.
        request = self._iress.DataManager.CreateOb(name)
        request.Clear()
        for k, v in params.iteritems():
            setattr(request, k, v) 

        self._do_request(request)
        log.debug('%i rows returned.', request.RowCount)

        # Return the results.
        results = []
        if request.RowCount > 0:
            fields = request.AvailableFields(False)
            for row in request.GetRows:
                results.append(dict(zip(fields, row)))
        return results

    def _do_request(self, request):
        request.Request()
        while self._wait_for_data(request):
            request.RequestNext()

    def _wait_for_data(self, request, timeout=DEFAULT_DATA_TIMEOUT):
        """
        Waits for data to be received from Iress. Returns True if
        another request is required.

        """

        running_time = 0

        while request.state == DfsCmd.constants.DataPending:
            time.sleep(REQUEST_POLL_INTERVAL)
            running_time += REQUEST_POLL_INTERVAL
            if running_time > timeout:
                raise IressError('Timed out waiting for data.')

        if request.state == DfsCmd.constants.DataReady:
            # Don't need to do anything if data is ready.
            return False
        elif request.state == DfsCmd.constants.Error:
            raise IressError(request.Error)
        elif request.state == DfsCmd.constants.DataIncomplete:
            raise IressError('Data was incomplete at the time of request.')
        elif request.state == DfsCmd.constants.DataMorePending:
            log.debug('More data required.')
            return True
        else:
            raise IressError('Unkown Error.')

if __name__ == '__main__':
    iress = IressDataClient()
    iress.connect()
    logging.basicConfig(level=logging.DEBUG)

    r= iress.execute(DfsIndicate.constants.dfsDataHistoricalMarketCapitalisation, dict(
        StartDate='01/05/2009',
        EndDate='01/05/2009',
        IndexFilter='XJO',
        Exchange='ASX',
    ))
    print len(r)

