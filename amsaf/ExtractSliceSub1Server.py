import SimpleITK as sitk
import os
from ExtractSliceFunction import ExtractSlices
"""
ExtractSlices(input_image, number_of_slices, axis):
"""




def main():
	#Get folders
	path30deg = "/srv/ultrasound_data/30deg/"

	path60deg = "/srv/ultrasound_data/60deg/"

	path90deg = "/srv/ultrasound_data/90deg/"

	result_directory_30deg_path = "/home/thomas/amsaf_results/30degslices/"

	result_directory_60deg_path = "/home/thomas/amsaf_results/60degslices/"

	result_directory_90deg_path = "/home/thomas/amsaf_results/90degslices/"

	for segmentation in os.listdir(path30deg):
		if segmentation.find("seg") >= 0:
			newfile = segmentation[:-4] + "_slices.nii"
			test = os.path.join(path30deg,segmentation)
			sitk.WriteImage(ExtractSlices(test, 10, 0),os.path.join(result_directory_30deg_path,newfile))
	
	for segmentation in os.listdir(path60deg):
		if segmentation.find("seg") >= 0:
			newfile = segmentation[:-4] + "_slices.nii"
			sitk.WriteImage(ExtractSlices(os.path.join(path60deg,segmentation), 10, 0),os.path.join(result_directory_60deg_path,newfile))
	
	for segmentation in os.listdir(path90deg):
		if segmentation.find("seg") >= 0:
			newfile = segmentation[:-4] + "_slices.nii"
			sitk.WriteImage(ExtractSlices(os.path.join(path90deg,segmentation), 10, 0),os.path.join(result_directory_90deg_path,newfile))

if __name__ == "__main__":
	main()
