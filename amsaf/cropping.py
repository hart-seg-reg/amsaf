
import os
from os.path import splitext, basename
import sys
import numpy as np
import amsaf
import SimpleITK as sitk
import heapq
from collections import Counter

#argparse?

def split_x(img, midpoint_x, padding=False):
	"""Splits image into two separate images along an x-plane
	Returns both halves of the image, returning the image with lower x values first

    :param img: Image to be split
    :param midpoint_x: x value specifying plane to split image along
    :param padding: Optional boolean to specify zero padding
    :type img: SimpleITK.Image
    :type midpoint_x: int
    :type padding: bool
    :rtype: (SimpleITK.Image, SimpleITK.Image)
    """
	data = sitk.GetArrayFromImage(img)
	if padding:
		data1 = np.zeros(data.shape)
		data2 = np.zeros(data.shape)
		data1[:, :, :midpoint_x] = data[:, :, :midpoint_x]
		data2[:, :, midpoint_x:] = data[:, :, midpoint_x:]
	else:
		data1 = data[:midpoint_x, :, :]
		data2 = data[midpoint_x:, :, :]

	crop1 = sitk.GetImageFromArray(data1)
	crop2 = sitk.GetImageFromArray(data2)
	return crop1, crop2

def split_y(img, midpoint_y, padding=False):
	"""Splits image into two separate images along an y-plane
	Returns both halves of the image, returning the image with lower y values first

    :param img: Image to be split
    :param midpoint_y: y value specifying plane to split image along
    :param padding: Optional boolean to specify zero padding
    :type img: SimpleITK.Image
    :type midpoint_y: int
    :type padding: bool
    :rtype: (SimpleITK.Image, SimpleITK.Image)
    """
	data = sitk.GetArrayFromImage(img)
	if padding:
		data1 = np.zeros(data.shape)
		data2 = np.zeros(data.shape)
		data1[:, :midpoint_y, :] = data[:, :midpoint_y, :]
		data2[:, midpoint_y:, :] = data[:, midpoint_y:, :]
	else:
		data1 = data[:, :midpoint_y, :]
		data2 = data[:, midpoint_y:, :]
	crop1 = sitk.GetImageFromArray(data1)
	crop2 = sitk.GetImageFromArray(data2)
	return crop1, crop2


def split_z(img, midpoint_z, padding=False):
	"""Splits image into two separate images along an z-plane
	Returns both halves of the image, returning the image with lower z values first

    :param img: Image to be split
    :param midpoint_z: z value specifying plane to split image along
    :param padding: Optional boolean to specify zero padding
    :type img: SimpleITK.Image
    :type midpoint_z: int
    :type padding: bool
    :rtype: (SimpleITK.Image, SimpleITK.Image)
    """
	data = sitk.GetArrayFromImage(img)
	if padding:
		data1 = np.zeros(data.shape)
		data2 = np.zeros(data.shape)
		data1[:midpoint_z, :, :] = data[:midpoint_z, :, :]
		data2[midpoint_z:, :, :] = data[midpoint_z:, :, :]
	else:
		data1 = data[:midpoint_z, :, :]
		data2 = data[midpoint_z:, :, :]
	crop1 = sitk.GetImageFromArray(data1)
	crop2 = sitk.GetImageFromArray(data2)
	return crop1, crop2

def crop(img, start, end, padding=False):
	"""Crops image along a bounding box specified by start and end

    :param img: Image to be cropped
    :param start: Tuple consisting of lower valued coordinates to define bounding box
    :param end: Tuple consisting of higher valued coordinates to define bounding box
    :param padding: Optional boolean to specify zero padding
    :type img: SimpleITK.Image
    :type start: (int, int, int)
    :type end: (int, int, int)
    :type padding: bool
    :rtype: SimpleITK.Image
    """
	data = sitk.GetArrayFromImage(img)
	if padding:
		new_array_data = np.zeros(data.shape)
		new_array_data[start[2]:end[2], start[1]:end[1], start[0]:end[0]] \
			= data[start[2]:end[2], start[1]:end[1], start[0]:end[0]]
	else:
		new_array_data = data[start[2]:end[2], start[1]:end[1], start[0]:end[0]]
	return sitk.GetImageFromArray(new_array_data)


	#NOTE: check to make sure x/y/z are correct order
def merge(img_size, pieces, k=10):
	data = np.zeros(img_size)
	storage = {}
	

	#Consolidate voxels from all images
	for start, piece in pieces:
		x1, y1, z1 = start
		piece = sitk.GetArrayFromImage(piece)
		x2, y2, z2 = piece.size
		for x in range(x2):
			for y in range(y2):
				for z in range(z2):
					location = (x + x1, y + y1, z + z2)
					if location in storage.keys()
						storage[location].append(piece[x, y, z])
					else:
						storage[location] = [piece[x, y, z]]
	

	#Fill in undisputed values and gather disputed
	disputed = {}
	undisputed = {}
	for x in range(img_size[0]):
		for y in range(img_size[1]):
			for z in range(img_size[2]):
				location = (x, y, z)
				if location not in storage.keys():
					data[x, y, z] = 0
				else if len(storage[location]) == 1:
					data[x, y, z] = storage[location][0]
					undisputed[location] = storage[location][0]
				else:
					disputed[location] = storage[location]


	#Consolidate overlapping voxels
	def consolidate(arr):
		return list(set(arr))

	for location in disputed.keys()
		pos = consolidate(disputed[location])
		if len(pos) == 0:
			data[location[0], location[1], location[2]] = 0
			undisputed[location] = 0
			del disputed[location]
		if len(pos) == 1:
			data[location[0], location[1], location[2]] = pos[0]
			undisputed[location] = pos[0]
			del disputed[location]
		else:
			disputed[location] = arr


	#Perform KNN
	def dist(val1, val2):
		return (val1[0] - val2[0])**2 + (val1[1] - val2[1])**2 \
					+ (val1[2] - val2[2])**2

	for location in disputed.keys()
		h = []

		for neighbor in undisputed.keys():
			h.append(dist(neighbor, location), undisputed[neighbor])
		heapq.heapify(h)

		nearby = Counter(heapq.nsmallest(k,h))

		data[location[0], location[1], location[2]]\
				= max(nearby, key=lambda x: nearby[x])


	#reconstruct and return image
	whole = sitk.GetImageFromArray(data)
	return whole



def main():
	if len(sys.argv) > 1:
		cmd = sys.argv[1]
		if cmd == "merge":


		elif cmd is not None:
			nifti_file = amsaf.read_image(sys.argv[1], True)
			start = [int(sys.argv[2]), int(sys.argv[4]), int(sys.argv[6])]
			end = [int(sys.argv[3]), int(sys.argv[5]), int(sys.argv[7])]
			output_file = sys.argv[8]
				
			amsaf.write_image(crop(img, start, end),output_file)
	
if __name__ == '__main__':
#	main()
	pass


