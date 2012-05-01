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
from typelibhelper import EnsureLatestVersion

log = logging.getLogger(__name__)

# Generate and import Python modules for the Iress typelibs.
DfsCmd = EnsureLatestVersion('{96EB07E1-03D0-11CF-B214-00AA002F2ED9}')
DfsPrice = EnsureLatestVersion('{DF120F00-A275-11D1-A122-0000F82508F6}')
DfsSec = EnsureLatestVersion('{AF802C80-B975-11D1-A138-0000F82508F6}')
DfsIndicate = EnsureLatestVersion('{9339DB61-1602-11D2-8FC4-0000F824C8AA}')
DfsTimeSeries = EnsureLatestVersion('{4832E620-C2AA-11D1-A143-0000F82508F6}')
DfsText = EnsureLatestVersion('{4FF26370-DEF3-11D1-A15F-0000F82508F6}')

# Default timeout when fetching data from Iress.
DEFAULT_DATA_TIMEOUT = 15

# Number of seconds to wait between polling data object's state.
REQUEST_POLL_INTERVAL = 0.2

class IressError(StandardError):
    pass

class IressRequestWrapper(object):
    """
    Abstract class that wraps an Iress automation
    CommandObject with a nicer Python interface.

    """
    def __init__(self, request):
        self._request = request

    def execute(self):
        """
        Derived classes should put their
        custom result handling here.

        """
        raise NotImplementedError()

    def _do_request(self):
        """
        Executes the actual request and polls Iress until
        all data has been received.

        """
        self._request.Request()
        while self._wait_for_data():
            self._request.RequestNext()
        log.debug('%i rows returned.', self._request.RowCount)

    def _wait_for_data(self, timeout=DEFAULT_DATA_TIMEOUT):
        """
        Waits for data to be received from Iress. Returns True if
        another request is required.

        """

        running_time = 0

        while self._request.state == DfsCmd.constants.DataPending:
            time.sleep(REQUEST_POLL_INTERVAL)
            running_time += REQUEST_POLL_INTERVAL
            if running_time > timeout:
                raise IressError('Timed out waiting for data.')

        if self._request.state == DfsCmd.constants.DataReady:
            # Don't need to do anything if data is ready.
            return False
        elif self._request.state == DfsCmd.constants.Error:
            raise IressError(self._request.Error)
        elif self._request.state == DfsCmd.constants.DataIncomplete:
            raise IressError('Data was incomplete at the time of request.')
        elif self._request.state == DfsCmd.constants.DataMorePending:
            log.debug('More data required.')
            return True
        else:
            raise IressError('Unkown Error.')

class DefaultRequestWrapper(IressRequestWrapper):
    """
    Returns the results of an Iress DataObject
    query as a dictionary.

    """
    def execute(self):
        self._do_request()

        results = []
        if self._request.RowCount > 0:
            fields = self._request.AvailableFields(False)
            results = [dict(zip(fields, row)) for row in self._request.GetRows]
        return results

class DataTextRequestWrapper(IressRequestWrapper):
    """
    Returns the result of an Iress DataText query
    as a list of strings.

    """
    def execute(self):
        self._do_request()
        return [self._request.TextLine(i) for i in range(self._request.RowCount)]

class DataTextHeadlineRequestWrapper(IressRequestWrapper):
    """
    Returns the result of an Iress DataTextHeadline
    query with special handing for the DataText
    property. 

    Each dictionary in the list of dictionaries returned
    from execute() will contain a DataTextRequestWrapper
    at the 'DataText' key. The rows in the data text
    can be accessed by calling the execute method on
    this wrapper object.

    """
    def execute(self):
        self._do_request()

        results = []
        if self._request.RowCount > 0:
            fields = self._request.AvailableFields(False)
            for index, row in enumerate(self._request.GetRows):
                result = dict(zip(fields, row))
                result['DataText'] = DataTextRequestWrapper(self._request.DataText(index))
                results.append(result)
        return results

# Specific Iress requests require special handling to extract all necessary
# data. This dictionary maps the request types to their special
# handling class.
REQUEST_WRAPPER_OVERRIDES = {
    DfsText.constants.dfsDataTextHeadline : DataTextHeadlineRequestWrapper,
}

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

    def execute(self, name, params, objects=()):
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

        # Find out if we need to wrap the request in a special wrapper; otherwise
        # just use the default wrapper.
        wrappercls = REQUEST_WRAPPER_OVERRIDES.get(name, DefaultRequestWrapper)
        log.debug('Using request wrapper %s.' % (wrappercls.__name__,))
        wrapper = wrappercls(request)

        return wrapper.execute()
        
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

