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
        while True:  # Main observation loop
            # Display observation table with numbered indices
            with np.printoptions(threshold=np.inf, linewidth=200):
                print("\nCurrent observations:")
                print("Index | ObsID | Target Name | Instrument | Filters | Calib Level")
                print("-" * 80)
                for idx, row in enumerate(obs_table):
                    print(f"[{idx}] | {row['obsid']} | {row['target_name']} | {row['instrument_name']} | {row['filters']} | {row['calib_level']}")

            try:
                # Ask user if they want to view filters
                view_filters = input("\nWould you like to view filters for an observation? (y/n): ").strip().lower()
                if view_filters != 'y':
                    break

                # Ask user which index they would like to choose from
                x = int(input("Please input the observation index: "))
                if x < 0 or x >= len(obs_table):
                    print("Invalid index. Please try again.")
                    continue

                obs_id = obs_table[x]['obsid']
                data_products = Observations.get_product_list(obs_id)
                fits_products = Observations.filter_products(
                    data_products,
                    extension="i2d.fits"
                )

                print(f"\nFound {len(fits_products)} FITS data products")
                if len(fits_products) > 0:
                    # Show all available products with index numbers
                    print("\nAvailable data products:")
                    for idx, product in enumerate(fits_products):
                        print(f"[{idx}] {product['productFilename']} - {product['productSubGroupDescription']} - {product['dataproduct_type']}")

                    # Multiple selection input
                    while True:
                        try:
                            indices_input = input("\nEnter the indices of files to download (comma-separated, e.g., '0,1,3')\nor 'all' for all files: ").strip()
                            
                            if indices_input.lower() == 'all':
                                selected_indices = list(range(len(fits_products)))
                            else:
                                selected_indices = [int(idx.strip()) for idx in indices_input.split(',')]
                            
                            # Verify indices
                            if all(0 <= idx < len(fits_products) for idx in selected_indices):
                                break
                            else:
                                print("One or more indices are out of range. Please try again.")
                        except ValueError:
                            print("Please enter valid numbers separated by commas.")

                    # Download selected products
                    for dp_index in selected_indices:
                        try:
                            print(f"\nDownloading product {dp_index + 1} of {len(selected_indices)}...")
                            download_info = Observations.download_products(fits_products[dp_index:dp_index+1])
                            fits_file_path = download_info['Local Path'][0]
                            print(f"Downloaded file: {fits_file_path}")

                            # Display the image
                            with fits.open(fits_file_path) as hdul:
                                hdul.info()
                                for i, hdu in enumerate(hdul):
                                    if hdu.data is not None:
                                        try:
                                            image_data = hdu.data
                                            print(f"\nImage shape: {image_data.shape}")
                                            print(f"Data min/max: {np.nanmin(image_data)}/{np.nanmax(image_data)}")
                                            plt.figure(figsize=(10, 8))
                                            plt.imshow(image_data, origin='lower',
                                                     norm=plt.Normalize(vmin=np.nanpercentile(image_data, 5),
                                                                         vmax=np.nanpercentile(image_data, 99)),
                                                     cmap='inferno')
                                            plt.colorbar(label='Brightness')
                                            plt.title(f"FITS Image - Product {dp_index}")
                                            plt.show()
                                            break
                                        except Exception as e:
                                            print(f"Could not display data from extension {i}: {e}")
                                else:
                                    print("No image data found in any extension.")
                        except Exception as e:
                            print(f"Error downloading or opening FITS file {dp_index}: {e}")
                            continue
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
    while True:  # Main program loop
        JWST_search(
            # objectname='Horsehead Nebula',  # Example object
            objectname=input("Please input the space object you're looking for: ")
            # obs_collection=input("Please input the mission name (e.g., 'JWST'): "),
            # instrument_name=input("Please input the instrument name (e.g., 'NIRCAM/IMAGE'): "),
            # dataRights=input("Please input the data rights (e.g., 'PUBLIC'): "),
            # dataproduct_type=input("Please input the data product type (e.g., 'image'): ")
        )
        again = input("Would you like to search for another object? (y/n): ").strip().lower()
        if again != 'y':
            print("Thank you for using Trevor's JWST search!")
            break    

# print(Observations.list_missions())

# objectname=input("Please input the space object you're looking for: ")
# obs_collection=input("Please input the mission name (e.g., 'JWST'): ")
# instrument_name=input("Please input the instrument name (e.g., 'NIRCAM/IMAGE'): ")
# dataRights=input("Please input the data rights (e.g., 'PUBLIC'): ")
# dataproduct_type=input("Please input the data product type (e.g., 'image'): ")

# execute(objectname, obs_collection, instrument_name, dataRights, dataproduct_type, calib_level='3')