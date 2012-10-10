"""
Dumps the database schema for all available IRESS ADO queries.

"""

from __future__ import print_function

from iress import ado

def main():
    client = ado.IressADOClient()
    client.connect()

    for catalog in client.get_catalogs():
        procedures = client.get_procedures(catalog)

        header = 'Catalog: {0}, {1} items'.format(catalog, len(procedures))
        print(header)
        print('='*len(header))

        for procedure in sorted(procedures):
            print('# {0}'.format(procedure))
            for (pname, ptype) in client.get_procedure_params(procedure):
                print ('\t{0} {1}'.format(pname, ptype))
        print()

if __name__ == '__main__':
    main()
