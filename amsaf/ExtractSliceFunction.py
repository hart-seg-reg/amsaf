import SimpleITK as sitk
import sys
import os

"""
Modified code from itk example ExtractSlice.py:
https://itk.org/gitweb?p=SimpleITK.git;a=blob;f=Examples/Python/ExtractSlice.py;h=51b793ab4d4030ad152ffea7bc8dce0f406a5567;hb=HEAD

How to Use:

python ExtractSliceFunction.py input_file number_of_slices output_file axis_of_slicing

arguments are as follows:
input_file: File that you want to obtain slices from
number_of_slices: Partitions input_file and makes equidistant slices along axis
    IMPORTANT NOTE:
        the number of slices partitions the whole image, not just the segmented part (a proportion of the slices may return empty vectors)
output_file: Name of output file
axis_of_slicing: Determines which plane slices align with (xy,yz,xz), Takes inputs 0,1,2 (else)

    Given an input file with dimensions [400,300,200]
    0 returns slices along x axis (slices of the form [x,300,200])
    1 returns slices along y axis (slices of the form [400,y,200])
    2 returns slices along z axis (slices of the form [400,300,z])

ExtraceSlices:
    Takes an input_image (.nii file), number of desired slices, and the axis with which to cut slices from, returns 32bitfloat nifti output image. 
"""

def ExtractSlices(input_image, number_of_slices, axis):
    
    sliceNum = int(number_of_slices)
    dim = int(axis)
    inputImage = sitk.ReadImage(str(input_image))
    
    size = list(inputImage.GetSize())
    
    output = sitk.Image(size[0], size[1], size[2],  sitk.sitkFloat32)
    
    if(dim == 0):
        length = int(size[0] / sliceNum)
        slices = [i for i in range(int(length / 2), size[0], length)]
        range1 = size[1]
        range2 = size[2]
    elif(dim == 1):
        length = int(size[1] / sliceNum)
    
        slices = [i for i in range(int(length / 2), size[1], length)]
        range1 = size[0]
        range2 = size[2]
    else:
        length = int(size[2] / sliceNum)
        slices = [i for i in range(int(length / 2), size[2], length)]
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
    return output
    
    
def main():
    if len ( sys.argv ) != 5:
        print("Usage: %s inputImage sliceNumber outputImage dimension" % (sys.argv[0]))
        sys.exit(1)
    output = ExtractSlices(sys.argv[1],sys.argv[2],sys.argv[4])
    sitk.WriteImage(output, str(sys.argv[3]))

if __name__ == "__main__":
    main()
