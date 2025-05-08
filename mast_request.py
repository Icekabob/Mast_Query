from utils import sys, json, requests, urlencode

def mast_query(request):
    """Perform a MAST query."""
    request_url = 'https://mast.stsci.edu/api/v0/invoke'
    version = ".".join(map(str, sys.version_info[:3]))
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
        "User-agent": f"python-requests/{version}"
    }
    req_string = json.dumps(request)
    req_string = urlencode(req_string)
    resp = requests.post(request_url, data="request=" + req_string, headers=headers)
    return resp.headers, resp.content.decode('utf-8')

def set_filters(parameters):
    return [{"paramName": p, "values": v} for p, v in parameters.items()]

def set_min_max(min_val, max_val):
    return [{'min': min_val, 'max': max_val}]
