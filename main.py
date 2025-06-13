from name_resolver import resolve_object
from mast_cone_search import cone_search
from get_products import get_observation_products, extract_science_products
from astroquery.mast import Observations

def main():
    object_name = 'NGC 6720'
    ra, dec = resolve_object(object_name)
    table = cone_search(ra, dec)

    # Create boolean mask for JWST observations
    jwst_mask = []
    for i in range(len(table)):
        if table['obs_collection'][i] == 'JWST':
            jwst_mask.append(True)
        else:
            jwst_mask.append(False)

    # Filter the table to get only JWST observations
    jwst_observations = table[jwst_mask]
    
    filter_name = "F150W2"  # Renamed for clarity
    
    # Process each JWST observation
    for obsid in jwst_observations['obsid']:
        obs_products = get_observation_products(obsid)
        science_products = extract_science_products(obs_products)
        # Download or further process science_products if needed
        
        obsid=obsid,
        product_type='SCIENCE',
        filter_name=filter_name
        )
if __name__ == "__main__":
    main()
