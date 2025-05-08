from mast_request import mast_query
from utils import json, pp

def resolve_object(object_name):
    resolver_request = {
        'service': 'Mast.Name.Lookup',
        'params': {'input': object_name, 'format': 'json'}
    }
    headers, resolved_object_string = mast_query(resolver_request)
    resolved_object = json.loads(resolved_object_string)
    pp.pprint(resolved_object)
    ra = resolved_object['resolvedCoordinate'][0]['ra']
    dec = resolved_object['resolvedCoordinate'][0]['decl']
    return ra, dec
