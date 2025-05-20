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
              'M57_f335m_i2d.fits']

              # 'M57_f212n_i2d.fits',  # filter not used
              
### sets the black point and white point in relative units for each filter
#
# if fblack = 0, the black point is set to the minimum pixel value
# if fblack = 0.1, the black point is set 10% above the minimum pixel value
# if fblack = 1.0, the black point is set to the MAX pixel value (not wise)
#
# if fwhite = 1.0, the white point is set to the MAX pixel value
# if fwhite = 0.5, the white point is set to half way between min and max values
#
fwhite = [0.0012, 0.0025,0.005]
fblack = [0.0006, 0.00045,0.0002]

# specify which filter should be used as the reference for coordinate transformations
ref_indx = 0   # use filter 0 (i.e. red) as the reference


#----------------  Read in i2d FITS  --------------------

# preallocate space for fits data
hdu    = [None] * len(fits_files)
header = [None] * len(fits_files)
data   = [None] * len(fits_files)
wcs    = [None] * len(fits_files)

# read in i2d fits files
for j in range(len(fits_files)):
    hdu[j] = fits.open(fits_files[j])
    header[j] = hdu[j]['SCI'].header
    data[j] = hdu[j]['SCI'].data
    wcs[j] = WCS(header[j])


#----------------  Project onto common coordinate frame  --------------------

# project files 1 and 2 onto coordinate system of file 0
if ref_indx == 0:
    R = data[0]
    G,_=reproject_interp((data[1], wcs[1]), wcs[0], shape_out=data[0].shape)
    B,_=reproject_interp((data[2], wcs[2]), wcs[0], shape_out=data[0].shape)
elif ref_indx == 1:
    G = data[1]
    R,_=reproject_interp((data[0], wcs[0]), wcs[1], shape_out=data[1].shape)
    B,_=reproject_interp((data[2], wcs[2]), wcs[1], shape_out=data[1].shape)
else:
    B = data[2]
    G,_=reproject_interp((data[1], wcs[1]), wcs[2], shape_out=data[2].shape)
    R,_=reproject_interp((data[0], wcs[0]), wcs[2], shape_out=data[2].shape)




# # Display the array as an image
# fig,ax = plt.subplots() 
# plt.imshow(a, cmap='gray',vmin=vmin+vrange*fblack[0],vmax=vmin+vrange*fblack[0]+vmax*f[0])  # Use a colormap like 'viridis', 'gray', etc.
# # plt.colorbar()  # Add a colorbar to show value-to-color mapping
# ax.set_axis_off()
# plt.title('comb')
# plt.show()
    
    

#----------------  Display raw tiff files  --------------------

for j,hd in enumerate(hdu):
    # print("image size = ",hd['SCI'].header['NAXIS2']," x ",hd['SCI'].header['NAXIS2']," pix arc sec ",np.sqrt(hd['SCI'].header['PIXAR_A2']))
    print("image size = ",header[j]['NAXIS2']," x ",header[j]['NAXIS2']," pix arc sec ",np.sqrt(header[j]['PIXAR_A2']))

    # get image data
    # data = hd['SCI'].data
    
    # find pixel value min, max and range
    vmin = np.nanmin(data[j])
    vmax = np.nanmax(data[j])
    vrange = vmax-vmin
    
    # Display the array as an image
    fig,ax = plt.subplots() 
    plt.imshow(data[j], cmap='gray',vmin=vmin+vrange*fblack[j],vmax=vmin+vrange*fwhite[j])  # Use a colormap like 'viridis', 'gray', etc.

    # plt.imshow(data[j], cmap='gray',vmin=vmin,vmax=vmin+vmax*f[j])  # Use a colormap like 'viridis', 'gray', etc.
    # plt.colorbar()  # Add a colorbar to show value-to-color mapping
    ax.set_axis_off()
    plt.title('Ring Nebula')
    plt.show()
    
    
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

# normalize each channel using to_unit16 function
r_16 = to_uint16(R,fblack[0],fwhite[0])
g_16 = to_uint16(G,fblack[1],fwhite[1])
b_16 = to_uint16(B,fblack[2],fwhite[2])

# Stack into RGB format: shape (H, W, 3)
rgb_16 = np.stack([r_16, g_16, b_16], axis=-1)

# Save 16-bit RGB TIFF
tifffile.imwrite('image_rgb_16bit.tiff', rgb_16)


#----------------  Display color filter combo  --------------------

# Display the array as an image
fig,ax = plt.subplots() 
plt.imshow(rgb_16.astype(float)/65535)  # Use a colormap like 'viridis', 'gray', etc.

ax.set_axis_off()
plt.title('Ring Nebula')
plt.show()
    
#----------------  plot histogram of each RGB filter  --------------------

plt.hist(r_16.flatten(),bins=50,color='r')
plt.hist(g_16.flatten(),bins=50,color='g')
plt.hist(b_16.flatten(),bins=50,color='b')
# # plt.grid(True)
plt.show()


    