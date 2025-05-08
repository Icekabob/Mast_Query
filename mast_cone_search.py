from mast_request import mast_query
from utils import json, pp, Table, np

def cone_search(ra, dec, radius=0.2, pagesize=2000, page=1):
    mast_request = {
        'service': 'Mast.Caom.Cone',
        'params': {'ra': ra, 'dec': dec, 'radius': radius},
        'format': 'json',
        'pagesize': pagesize,
        'page': page,
        'removenullcolumns': True,
        'removecache': True
    }
    headers, mast_data_str = mast_query(mast_request)
    mast_data = json.loads(mast_data_str)
    print("Query status:", mast_data['status'])
    pp.pprint(mast_data['fields'][:5])
    table = Table()
    for col, atype in [(x['name'], x['type']) for x in mast_data['fields']]:
        if atype == "string":
            atype = "str"
        if atype == "boolean":
            atype = "bool"
        table[col] = np.array([x.get(col, None) for x in mast_data['data']], dtype=atype)
    print(table)
    return table
