from name_resolver import resolve_object
from mast_cone_search import cone_search
from get_products import get_observation_products, extract_science_products

def main():
    object_name = 'M50'
    ra, dec = resolve_object(object_name)
    table = cone_search(ra, dec)
    interesting_obs = table[table["obs_collection"] == "JWST"][0]
    obsid = interesting_obs['obsid']
    obs_products = get_observation_products(obsid)
    science_products = extract_science_products(obs_products)
    # Download or further process science_products if needed

if __name__ == "__main__":
    main()
