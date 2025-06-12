from astroquery.mast import Observations
from astropy.io import fits
from astropy.table import conf
import matplotlib.pyplot as plt
import numpy as np
from mcp.server.fastmcp import FastMCP
from typing import Any
import httpx

mcp = FastMCP("JWST")
#define mcp tool
@mcp.tool()
def JWST_search(objectname, obs_collection='JWST', instrument_name='NIRCAM/IMAGE', dataRights='PUBLIC', dataproduct_type='image', calib_level=3):
    """Execute a search for JWST observations and download FITS files.
    
    Args:
        objectname (str): Name of the astronomical object to search for.
        obs_collection (str): Name of the observation collection (default is 'JWST').
        instrument_name (str): Name of the instrument (default is 'NIRCAM/IMAGE').
        dataRights (str): Data rights (default is 'PUBLIC').
        dataproduct_type (str): Type of data product to search for (default is 'image').
        calib_level (int): Calibration level to filter observations (default is 3).
    """
    conf.max_lines = 1000   # or any large number
    conf.max_width = 500    # or any large number

    obs_collection = obs_collection.upper()  # Ensure collection name is uppercase
    instrument_name = instrument_name.upper()  # Ensure instrument name is uppercase
    dataRights = dataRights.upper()  # Ensure data rights is uppercase

    obs_table = Observations.query_criteria(
        objectname=objectname,
        obs_collection=obs_collection,
        instrument_name=instrument_name,
        dataRights=dataRights,
        dataproduct_type=dataproduct_type,
        calib_level=calib_level
    )
    print("Searching for tables")
    print(f"Found {len(obs_table)} observations")
    if len(obs_table) > 0:
        # Print the entire table without truncation
        with np.printoptions(threshold=np.inf, linewidth=200):
            print(obs_table['obsid', 'target_name', 'instrument_name', 'filters', 'calib_level'])

        while True:
            try:
                #Ask user which index they would like to choose from
                x = int(input("Please input the index: "))
                obs_id = obs_table[x]['obsid']
                data_products = Observations.get_product_list(obs_id)
                fits_products = Observations.filter_products(
                    data_products,
                    #Filter products based on image 2 dimension flexible image
                    extension="i2d.fits"
                )

                print(f"\nFound {len(fits_products)} FITS data products")
                if len(fits_products) > 0:
                    # Show up to 50 results, or all if fewer
                    print(fits_products['productFilename', 'productSubGroupDescription', 'dataproduct_type'])

                    # Dataproduct selector
                    while True:
                        try:
                            dp_index = int(input(f"Select the data product index (0-{len(fits_products)-1}): "))
                            if 0 <= dp_index < len(fits_products):
                                break
                            else:
                                print("Index out of range.")
                        except ValueError:
                            print("Please enter a valid integer.")

                    try:
                    #Download data product and save it to mastDownload folder for later
                        download_info = Observations.download_products(fits_products[dp_index:dp_index+1])
                        fits_file_path = download_info['Local Path'][0]
                        print(f"\nDownloaded file: {fits_file_path}")

                        with fits.open(fits_file_path) as hdul:
                            hdul.info()
                            for i, hdu in enumerate(hdul):
                                if hdu.data is not None:
                                    try:
                                        #Open fits file and display the image data
                                        image_data = hdu.data
                                        print(f"\nImage shape: {image_data.shape}")
                                        print(f"Data min/max: {np.nanmin(image_data)}/{np.nanmax(image_data)}")
                                        plt.figure(figsize=(10, 8))
                                        plt.imshow(image_data, origin='lower',
                                                norm=plt.Normalize(vmin=np.nanpercentile(image_data, 5),
                                                                    vmax=np.nanpercentile(image_data, 99)),
                                                cmap='inferno')
                                        plt.colorbar(label='Brightness')
                                        plt.title(f"FITS Image")
                                        plt.show()
                                        break
                                    except Exception as e:
                                        print(f"Could not display data from extension {i}: {e}")
                            else:
                                print("No image data found in any extension.")
                        break  # Success, exit the retry loop
                    except Exception as e:
                        print(f"Error downloading or opening FITS file: {e}")
                        retry = input("Download/open failed. Try another index? (y/n): ").strip().lower()
                        if retry != 'y':
                            break
                else:
                    print("No FITS files found for this observation.")
                    retry = input("Try another index? (y/n): ").strip().lower()
                    if retry != 'y':
                        break
            except Exception as e:
                print(f"Error: {e}")
                retry = input("Try another index? (y/n): ").strip().lower()
                if retry != 'y':
                    break
    else:
        print("No observations found. Try a different search approach.")

if __name__ == "__main__":
    # Initialize and run the server
    # mcp.run(transport='stdio')
    JWST_search(
        # objectname='Horsehead Nebula',  # Example object
        objectname=input("Please input the space object you're looking for: ")
        # obs_collection=input("Please input the mission name (e.g., 'JWST'): "),
        # instrument_name=input("Please input the instrument name (e.g., 'NIRCAM/IMAGE'): "),
        # dataRights=input("Please input the data rights (e.g., 'PUBLIC'): "),
        # dataproduct_type=input("Please input the data product type (e.g., 'image'): ")
    )

# print(Observations.list_missions())

# objectname=input("Please input the space object you're looking for: ")
# obs_collection=input("Please input the mission name (e.g., 'JWST'): ")
# instrument_name=input("Please input the instrument name (e.g., 'NIRCAM/IMAGE'): ")
# dataRights=input("Please input the data rights (e.g., 'PUBLIC'): ")
# dataproduct_type=input("Please input the data product type (e.g., 'image'): ")

# execute(objectname, obs_collection, instrument_name, dataRights, dataproduct_type, calib_level='3')