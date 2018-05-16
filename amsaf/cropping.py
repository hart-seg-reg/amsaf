
"""
Usage:

python3 name_of_image_to_be_cropped x_dimension_start x_dimension_end y_dimension_start y_dimension_end	z_dimension_start z_dimension_end output_file_name

"""
import os
import sys
import numpy as np
from nibabel.testing import data_path
import nibabel as nib

#input file
#file = sys.argv[1]
img = nib.load(sys.argv[1])
data = img.get_data()

#data is a 3d numpy array with dimensions x,y,z 
#length of arm, height of arm, cross section of arm

#should only need x dimension
# we will 0 out anything that is past a certain point
def prototype_cropper(nifti_file, x_dimension):
	#array is a 3 dim array
	numpy_array_data = nifti_file.get_data()
	for i in range(x_dimension+1, len(numpy_array_data)):
		numpy_array_data[i] = 0
	return nib.Nifti1Image(numpy_array_data,nifti_file.affine)

def cropper_no_zero_padding(
	nifti_file, x_dimension_start, x_dimension_end, 
	y_dimension_start, y_dimension_end, 
	z_dimension_start, z_dimension_end):
	return nib.Nifti1Image(nifti_file.get_data()[x_dimension_start:x_dimension_end][y_dimension_start:y_dimension_end][z_dimension_start:z_dimension_end],nifti_file.affine)

def cropper_with_zero_padding(
	nifti_file, x_dimension_start, x_dimension_end, 
	y_dimension_start, y_dimension_end, 
	z_dimension_start, z_dimension_end):
	numpy_array_data = nifti_file.get_data()
	new_array_data = np.zeros(numpy_array_data.shape)
	for i in range(x_dimension_start,x_dimension_end):
		for j in range(y_dimension_start,y_dimension_end):
			for k in range(z_dimension_start,z_dimension_end):
				new_array_data[i,j,k] = numpy_array_data[i,j,k]
	return nib.Nifti1Image(new_array_data,nifti_file.affine)


def main():
	nifti_file = nib.load(sys.argv[1])
	x_dimension_start = int(sys.argv[2])
	x_dimension_end = int(sys.argv[3]) - 1
	y_dimension_start = int(sys.argv[4])
	y_dimension_end = int(sys.argv[5]) - 1
	z_dimension_start = int(sys.argv[6])
	z_dimension_end = int(sys.argv[7]) - 1
	output_file = sys.argv[8]
	
	nib.save(cropper_no_zero_padding(nifti_file, x_dimension_start, x_dimension_end, 
	y_dimension_start, y_dimension_end, 
	z_dimension_start, z_dimension_end),output_file)

	#nib.save(cropper_with_zero_padding(nifti_file, x_dimension_start, x_dimension_end, 
	#y_dimension_start, y_dimension_end, 
	#z_dimension_start, z_dimension_end),output_file)

if __name__ == '__main__':
	main()