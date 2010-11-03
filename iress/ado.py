"""
Pythonic interface to the ADO stored procedures exposed
by the Iress Portfolio System (IPS).

"""

import win32com.client
import pywintypes

def convert_com_dates_to_mx(records):
    import mx.DateTime
    for d in records:
        for k in d:
            if isinstance(d[k], pywintypes.TimeType):
                d[k] = mx.DateTime.DateTimeFromCOMDate(d[k])
    return records

def _extract_recordset(recordset):
    """
    Converts a ADODB.RecordSet object into a list
    of Python dictionaries.

    """
    records = []
    count = recordset.Fields.Count
    keys = [recordset.Fields(i).Name for i in range(count)]
    while not recordset.EOF:
        records.append(dict(zip(
            keys,
            [recordset.Fields(i).Value for i in range(count)])))
        recordset.MoveNext()
    return records

class IressADOClient(object):
    """
    Pythonic wrapper around the IRESS OleDB API.

    """
    def __init__(self):
        self.c = None

    def connect(self):
        """
        Connects to the IRESS database, this method
        must be called prior to any other methods.

        """
        assert self.c is None, 'Already connected.'
        self.c = win32com.client.Dispatch('ADODB.Connection')
        self.c.Provider = 'IRESSOleDBProvider.IOleDBP.1'
        self.c.Open()

    def get_procedures(self):
        """
        Returns a list of the available stored procedures.

        """
        rs = self.c.OpenSchema(16, ['IPS'])
        return [record['PROCEDURE_NAME'] for record in _extract_recordset(rs)]

    def get_procedure_params(self, procedure):
        """
        Gets the list of parameters for a given stored procedure.

        """
        cmd = self._create_command(procedure)
        cmd.Parameters.Refresh()

        parameters = [cmd.Parameters(i).Name for i in range(cmd.Parameters.Count)]
        parameters.sort()
        return parameters

    def _create_command(self, procedure):
        """
        Create an ADODB.Command object prepared to call
        a stored procedure.

        """
        cmd = win32com.client.Dispatch('ADODB.Command')
        cmd.CommandType = 4
        cmd.CommandText = procedure
        cmd.ActiveConnection = self.c

        return cmd

    def execute_procedure(self, procedure, parameters=None):
        """
        Executes a stored procedure pasing in the given
        parameters.

        """
        parameters = parameters or {}
        cmd = self._create_command(procedure)

        for k, v in parameters.iteritems():
            cmd.Parameters(procedure.lower() + '_' + k.lower()).Value = v

        rs, count = cmd.Execute()
        return _extract_recordset(rs)
