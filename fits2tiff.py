# Program to read i2d fits files containing images from the 
# James Webb Space Telescope (JWST) to create false-color 
# images. 

from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
import tifffile
import matplotlib.pyplot as plt
import numpy as np


#----------------  User Defined Input  --------------------

#  list of i2d JWST fits files in RGB order
fits_files = ['M57_f150w2_i2d.fits',
              'M57_f300m_i2d.fits',
              'M57_f335m_i2d.fits',
              'M57_f212n_i2d.fits']
              
### sets the black point and white point in relative units for each filter
#
# if fblack = 0, the black point is set to the minimum pixel value
# if fblack = 0.1, the black point is set 10% above the minimum pixel value
# if fblack = 1.0, the black point is set to the MAX pixel value (not wise)
#
# if fwhite = 1.0, the white point is set to the MAX pixel value
# if fwhite = 0.5, the white point is set to half way between min and max values
#
fwhite = 0.01 #[0.0012, 0.005,0.0075,0.003]
fblack = 0    #[0.0006, 0.00045,0.0002,0.0006]

# specify which filter should be used as the reference for coordinate transformations
ref_indx = 0   # use filter 0 (i.e. red) as the reference


#----------------  Read in i2d FITS  --------------------

# preallocate space for fits data
hdu       = [None] * len(fits_files)
header    = [None] * len(fits_files)
data      = [None] * len(fits_files)
data_grid = [None] * len(fits_files)
wcs       = [None] * len(fits_files)

# read in i2d
for j in range(len(fits_files)):
    print("reading in "+fits_files[j])
    hdu[j] = fits.open(fits_files[j])
    header[j] = hdu[j]['SCI'].header
    data[j] = hdu[j]['SCI'].data
    wcs[j] = WCS(header[j])


#----------------  Project onto common coordinate frame  --------------------

print("\nprojecting onto a common coordinate system")
# project files onto coordinate system of file ref_indx
for j in range(len(fits_files)):
    print("  "+fits_files[j])
    if j == ref_indx:
        data_grid[ref_indx] = data[ref_indx]
    else:
        data_grid[j] = reproject_interp((data[j], wcs[j]), wcs[ref_indx], shape_out=data[ref_indx].shape)




print("ok")

#----------------  Display raw tiff files  --------------------

# for j,hd in enumerate(hdu):
#     # print("image size = ",hd['SCI'].header['NAXIS2']," x ",hd['SCI'].header['NAXIS2']," pix arc sec ",np.sqrt(hd['SCI'].header['PIXAR_A2']))
#     print("image size = ",header[j]['NAXIS2']," x ",header[j]['NAXIS2']," pix arc sec ",np.sqrt(header[j]['PIXAR_A2']))

#     # get image data
#     # data = hd['SCI'].data
    
#     # find pixel value min, max and range
#     vmin = np.nanmin(data[j])
#     vmax = np.nanmax(data[j])
#     vrange = vmax-vmin
    
#     # Display the array as an image
#     fig,ax = plt.subplots() 
#     plt.imshow(data[j], cmap='gray',vmin=vmin+vrange*fblack[j],vmax=vmin+vrange*fwhite[j])  # Use a colormap like 'viridis', 'gray', etc.

#     # plt.imshow(data[j], cmap='gray',vmin=vmin,vmax=vmin+vmax*f[j])  # Use a colormap like 'viridis', 'gray', etc.
#     # plt.colorbar()  # Add a colorbar to show value-to-color mapping
#     ax.set_axis_off()
#     plt.title('Ring Nebula')
#     plt.show()
    
    
#----------------  Convert to tiff file  --------------------

# normalize each channel to range 0 - 65535 for 16-bit tiff
#
def to_uint16(channel,fblk,fwht):
    # find pixel value min, max and range
    vmin = np.nanmin(channel)
    vmax = np.nanmax(channel)
    vrange = vmax-vmin
    
    # replace missing pixel values with 0
    channel = np.nan_to_num(channel)

    # calculate black and white points
    blk = vmin + vrange*fblk
    wht = vmin + vrange*fwht
    
    # ensure pixel values are between black and white point
    norm = channel
    norm[norm<blk] = blk
    norm[norm>wht] = wht
    
    # return image with pixel values between 0 - 65535 
    norm = (norm - blk) / (wht - blk + 1e-6)
    return (norm * 65535).astype(np.uint16)


#----------------  normalize each channel using to_unit16 function  --------------------
print("\nStretching pixel values to ")
# fblack sets the black point (as a fraction)
# fwhite sets the white point (as a fraction)
for j in range(len(fits_files)):
    data_grid[j] = to_uint16(data_grid[j],fblack,fwhite)
    
    
#----------------  write file as a .tif  --------------------

for j in range(len(fits_files)):
    file_out = (fits_files[j].rstrip(".fit")).rstrip(".fits")
    print("saving "+file_out+" as .tif file")
    tifffile.imwrite(file_out+".tiff",data_grid[j])
    
    





    