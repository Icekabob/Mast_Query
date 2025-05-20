from astroquery.mast import Observations
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Search for observations
# Let's try a more specific approach - using the object name "NGC 6720" (catalog name for M57)
obs_table = Observations.query_criteria(
    objectname="NGC 6720",  # Alternative name for M57/Ring Nebula
    obs_collection="JWST"
)
x=Observations.get_metadata("observation")
print(x)
# Print basic info to verify we found observations
print(f"Found {len(obs_table)} observations")
if len(obs_table) > 0:
    print(obs_table['obsid', 'target_name', 'instrument_name', 'filters'][:5])  # First 5 results

    # Step 2: Get data products for a specific observation
    # Choose an observation by its index (e.g., 0 for the first one)
    obs_id = obs_table[0]['obsid']  # Get the observation ID
    data_products = Observations.get_product_list(obs_id)
    
    # Filter for Level 2 or 3 calibrated science products, focusing on FITS files
    science_products = Observations.filter_products(
        data_products,
        productType="SCIENCE",
        extension="fits"
    )
    
    # Show what's available
    print(f"\nFound {len(science_products)} science data products")
    if len(science_products) > 0:
        print(science_products['productFilename', 'productSubGroupDescription', 'dataproduct_type'][:5])
    
    # Step 3: Download the files you need
    # You can download all files, but let's select specific ones by index
    if len(science_products) > 0:
        # Let's download the first science product as an example
        download_info = Observations.download_products(science_products[0:1])
        
        # Get the path to the downloaded file
        fits_file_path = download_info['Local Path'][0]
        print(f"\nDownloaded file: {fits_file_path}")
        
        # Step 4: Open and work with the FITS file
        with fits.open(fits_file_path) as hdul:
            # Print information about the file structure
            hdul.info()
            
            # Determine which HDU contains the science data (usually 1 for JWST)
            # This can vary based on the specific product, so we need to check
            science_hdu = 1  # Default, but could be different
            
            # Access the data array
            try:
                image_data = hdul[science_hdu].data
                
                # Display basic stats about the data
                print(f"\nImage shape: {image_data.shape}")
                print(f"Data min/max: {np.nanmin(image_data)}/{np.nanmax(image_data)}")
                
                # Create a simple visualization
                plt.figure(figsize=(10, 8))
                # Use log scale for visualization as astronomical data often has high dynamic range
                plt.imshow(image_data, origin='lower', 
                           norm=plt.Normalize(vmin=np.nanpercentile(image_data, 5), 
                                             vmax=np.nanpercentile(image_data, 99)),
                           cmap='inferno')
                plt.colorbar(label='Brightness')
                plt.title(f"JWST Image of M57 (Ring Nebula)")
                plt.show()
                
            except (IndexError, TypeError):
                print("Couldn't find science data in expected extension. Try a different one.")
                # List available extensions to help identify which contains the data
                for i, ext in enumerate(hdul):
                    print(f"Extension {i}: {ext.name} - {type(ext.data)}")
else:
    print("No observations found. Try a different search approach.")