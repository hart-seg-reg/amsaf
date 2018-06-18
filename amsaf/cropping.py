
"""
Usage:

python3 name_of_image_to_be_cropped x_dimension_start x_dimension_end y_dimension_start y_dimension_end	z_dimension_start z_dimension_end output_file_name

"""
import os
import sys
import numpy as np
from nibabel.testing import data_path
import nibabel as nib

#data is a 3d numpy array with dimensions x,y,z 
#length of arm, height of arm, cross section of arm

def split(nifti_file, start, mid, end):
	data = nifti_file.get_data()
	if zero_padding:
		new_array_data1 = np.zeros(numpy_array_data.shape)
		new_array_data2 = np.zeros(numpy_array_data.shape)
		new_array_data1[start[0]:mid[0], start[1]:mid[1], start[2]:mid[2]] \
			= data[start[0]:mid[0], start[1]:mid[1], start[2]:mid[2]]
		new_array_data2[mid[0]:end[0], mid[1]:end[1], mid[2]:end[2]] \
			= data[mid[0]:end[0], mid[1]:end[1], mid[2]:end[2]]
	else:
		new_array_data1 = data[start[0]:mid[0], start[1]:mid[1], start[2]:mid[2]]
		new_array_data2 = data[mid[0]:end[0], mid[1]:end[1], mid[2]:end[2]]
	return (nib.Nifti1Image(new_array_data1, nifti_file.affine),\
			nib.Nifti1Image(new_array_data2, nifti_file.affine))


def crop(nifti_file, start, end, zero_padding=False):
	data = nifti_file.get_data()
	if zero_padding:
		new_array_data = np.zeros(numpy_array_data.shape)
		new_array_data[start[0]:end[0], start[1]:end[1], start[2]:end[2]] \
			= data[start[0]:end[0], start[1]:end[1], start[2]:end[2]]
	else:
		new_array_data = data[start[0]:end[0], start[1]:end[1], start[2]:end[2]]
	return nib.Nifti1Image(new_array_data, nifti_file.affine)



def main():
	cmd = sys.argv[1]
	if cmd == "crop":
		if sys.argc == 2:

		else:
			nifti_file = nib.load(sys.argv[2])
			start = [int(sys.argv[3]), int(sys.argv[5]), int(sys.argv[7])]
			end = [int(sys.argv[4]), int(sys.argv[6]), int(sys.argv[8])]
			output_file = sys.argv[9]
	elif cmd == "split"
	
	nib.save(crop(nifti_file, start, end),output_file)

	#nib.save(cropper_with_zero_padding(nifti_file, x_dimension_start, x_dimension_end, 
	#y_dimension_start, y_dimension_end, 
	#z_dimension_start, z_dimension_end),output_file)

if __name__ == '__main__':
	main()