from mast_request import mast_query
from utils import json, pp, Table, np

def get_observation_products(obsid):
    product_request = {
        'service': 'Mast.Caom.Products',
        'params': {'obsid': obsid},
        'format': 'json',
        'pagesize': 100,
        'page': 1
    }
    headers, obs_products_string = mast_query(product_request)
    obs_products = json.loads(obs_products_string)
    print("Number of data products:", len(obs_products["data"]))
    pp.pprint(obs_products['fields'])
    return obs_products

def extract_science_products(obs_products):
    sci_prod_arr = [x for x in obs_products['data'] if x.get("productType", None) == 'SCIENCE']
    science_products = Table()
    for col, atype in [(x['name'], x['type']) for x in obs_products['fields']]:
        if atype == "string":
            atype = "str"
        if atype == "boolean":
            atype = "bool"
        science_products[col] = np.array([x.get(col, None) for x in sci_prod_arr], dtype=atype)
    print(science_products)
    return science_products
