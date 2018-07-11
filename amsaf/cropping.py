
"""
Usage:

python3 name_of_image_to_be_cropped x_dimension_start x_dimension_end y_dimension_start y_dimension_end	z_dimension_start z_dimension_end output_file_name

"""
import os
from os.path import splitext, basename
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
	return nib.Nifti1Image(new_array_data1, nifti_file.affine),\
			nib.Nifti1Image(new_array_data2, nifti_file.affine)



def split_x(f, midpoint_x, save=False):
	nifti_file = nib.load(f)
	data = nifti_file.get_data()
	outname1 = splitext(basename(f))[0] + "_crop1.nii"
	outname2 = splitext(basename(f))[0] + "_crop2.nii"
	data1 = data[:midpoint_x, :, :]
	data2 = data[midpoint_x:, :, :]
	crop1 = nib.Nifti1Image(data1, nifti_file.affine)
	crop2 = nib.Nifti1Image(data2, nifti_file.affine)
	if save:
		nib.save(crop1, outname1)
		nib.save(crop2, outname2)
	else:
		return crop1, crop2

def split_y(f, midpoint_y, save=False):
	nifti_file = nib.load(f)
	data = nifti_file.get_data()
	outname1 = splitext(basename(f))[0] + "_crop1.nii"
	outname2 = splitext(basename(f))[0] + "_crop2.nii"
	data1 = data[:, :midpoint_y, :]
	data2 = data[:, midpoint_y:, :]
	crop1 = nib.Nifti1Image(data1, nifti_file.affine)
	crop2 = nib.Nifti1Image(data2, nifti_file.affine)
	if save:
		nib.save(crop1, outname1)
		nib.save(crop2, outname2)
	else:
		return crop1, crop2


def split_z(f, midpoint_z, save=False):
	nifti_file = nib.load(f)
	data = nifti_file.get_data()
	outname1 = splitext(basename(f))[0] + "_crop1.nii"
	outname2 = splitext(basename(f))[0] + "_crop2.nii"
	data1 = data[:, :, :midpoint_z]
	data2 = data[:, :, midpoint_z:]
	crop1 = nib.Nifti1Image(data1, nifti_file.affine)
	crop2 = nib.Nifti1Image(data2, nifti_file.affine)
	if save:
		nib.save(crop1, outname1)
		nib.save(crop2, outname2)
	else:
		return crop1, crop2




def merge(size, pieces, outfile=None):
	data = np.zeros(size)
	count = np.zeros(size)
	for start, piece in pieces:
		x, y, z = start
		piece = piece.get_data()
		x2, y2, z2 = piece.size
		data[x:x2, y:y2, z:z2] += piece[:,:,:]
		count[x:x2, y:y2, z:z2] += 1
	for x in range(size[0]):
		for y in range(size[1]):
			for z in range(size[2]):
				if data[x, y, z] != 0:
					count[x, y, z] /= data[x, y, z]

	whole = nib.Nifti1Image(data, nifti_file.affine)
	if outfile is not None:
		nib.save(whole, outfile)
	else: 
		return whole


def crop(nifti_file, start, end, zero_padding=False):
	data = nifti_file.get_data()
	if zero_padding:
		new_array_data = np.zeros(numpy_array_data.shape)
		new_array_data[start[0]:end[0], start[1]:end[1], start[2]:end[2]] \
			= data[start[0]:end[0], start[1]:end[1], start[2]:end[2]]
	else:
		new_array_data = data[start[0]:end[0], start[1]:end[1], start[2]:end[2]]
	return nib.Nifti1Image(new_array_data, nifti_file.affine)


'''
def main():
	cmd = sys.argv[1]
	if cmd == "split":
		if len(sys.argv) == 4:
			split_x(sys.argv[2], int(sys.argv[3]))
	elif cmd == "merge":
		size = (1,2,3)
		pieces = []
		outfile = "testing"

	else:
		nifti_file = nib.load(sys.argv[1])
		start = [int(sys.argv[2]), int(sys.argv[4]), int(sys.argv[6])]
		end = [int(sys.argv[3]), int(sys.argv[5]), int(sys.argv[7])]
		output_file = sys.argv[8]
			
		nib.save(crop(nifti_file, start, end),output_file)

	#nib.save(cropper_with_zero_padding(nifti_file, x_dimension_start, x_dimension_end, 
	#y_dimension_start, y_dimension_end, 
	#z_dimension_start, z_dimension_end),output_file)

if __name__ == '__main__':
	main()

	'''

	