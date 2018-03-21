import SimpleITK as sitk
import sys
import os

"""
How to Use:
example: python ExtractSlice.py /data/trial11_30_w2_seg_TRANS.nii 9 /data/try.nii 0
/data/trial11_30_w2_seg_TRANS.nii : input segmentation path
9 : The number of slices extract from the input segmentation
/data/try : the output slices 
0 : in which dimension the slices will be extracted, e.g. if the input image size is [400, 300, 200]
    if this parameter is 0, each slices will be [1, 300, 200]
    if this parameter is 1, each slices will be [400, 1, 200]
    if this parameter is 2, each slices will be [400, 300, 1]
"""

if len ( sys.argv ) != 5:
    print("Usage: %s inputImage sliceNumber outputImage" % (sys.argv[0]))
    sys.exit(1)

sliceNum = int(sys.argv[2])
dim = int(sys.argv[4])
inputImage = sitk.ReadImage(str(sys.argv[1]))

size = list(inputImage.GetSize())

output = sitk.Image(size[0], size[1], size[2],  sitk.sitkFloat32)

if(dim == 0):
    length = size[0] / sliceNum
    slices = [i for i in range(length / 2, size[0], length)]
    range1 = size[1]
    range2 = size[2]
elif(dim == 1):
    length = size[1] / sliceNum
    slices = [i for i in range(length / 2, size[1], length)]
    range1 = size[0]
    range2 = size[2]
else:
    length = size[2] / sliceNum
    slices = [i for i in range(length / 2, size[2], length)]
    range1 = size[0]
    range2 = size[1]

for i in range(range1):
    for j in range(range2):
        for index in slices:
            if(dim == 0):
                temp = inputImage.GetPixel(index, i, j)
                output.SetPixel(index, i, j, temp)
            elif(dim == 1):
                temp = inputImage.GetPixel(i, index,j)
                output.SetPixel(i, index, j, temp)
            else:
                temp = inputImage.GetPixel(i, j, index)
                output.SetPixel(i, j, index, temp)

sitk.WriteImage(output, str(sys.argv[3]) )