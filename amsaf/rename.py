from os import listdir
from os.path import isfile, join, basename, splitext
import sys
import SimpleITK as sitk

def rename(path):
	files = [f for f in listdir(path) if isfile(join(path, f))]

	for f in files:
		outname = splitext(basename(f))[0] + ".nii"
		img = sitk.ReadImage(join(path, f))
		sitk.WriteImage(img, join(path, outname))


if __name__ == "__main__":
	[rename(sys.argv[i]) for i in range(1,len(sys.argv))]
