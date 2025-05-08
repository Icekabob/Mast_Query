from mast_request import mast_query
from utils import json, pp

def filtered_count(filters):
    mashup_request = {
        "service": "Mast.Caom.Filtered",
        "format": "json",
        "params": {
            "columns": "COUNT_BIG(*)",
            "filters": filters
        }
    }
    headers, out_string = mast_query(mashup_request)
    count = json.loads(out_string)
    pp.pprint(count)
    return count

def filtered_query(filters):
    mashup_request = {
        "service": "Mast.Caom.Filtered",
        "format": "json",
        "params": {
            "columns": "*",
            "filters": filters
        }
    }
    headers, out_string = mast_query(mashup_request)
    data = json.loads(out_string)
    print("Query status:", data['status'])
    pp.pprint(data['data'][0])
    return data
