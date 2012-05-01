"""
Example usage of iress.IressDataClient that fetches company
announcement data for 2008.

A full list of the data available via the iress API is listed in
the IRESS Automation Reference; Help -> Automation Reference.

"""

import logging
from iress import IressDataClient, DfsText

def main():
    idc = IressDataClient()
    idc.connect()

    announcements = idc.execute(DfsText.constants.dfsDataTextHeadline, dict(
        Code='BHP',
        StartDateTime='2008-01-01',
        EndDateTime='2009-01-01',
    ))

    # Only consider market sensitive announcemens.
    market_sensitive = [x for x in announcements if x['MarketSensitive'] == 'Y']
    for index, headline in enumerate(market_sensitive):
        print '%d: %s' % (index, headline['Headline'])
        print headline['GMTDate']
        bodytext = '\n'.join(headline['DataText'].execute())

        # Write out body text stripping non-ascii unicode. Iress
        # returns text as unicode but the Windows prompt
        # doesn't seem to like UTF-8!
        print bodytext.encode('ascii', 'ignore')

        # Only print first 20 announcements beacuse we're hitting
        # Iress for every bodytext request.
        if index > 20:
            break

if __name__ == '__main__':
    main()

