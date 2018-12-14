
import numpy as np
import csv
import sys
import os
import SimpleITK as sitk
import xlrd


"""
File to run affine transforms on sitk images

Required dependencies: SimpleElastix, Numpy

Main code of file is contained in run().

Modify parameters at bottom of file to change inputs of run.

Documentation of parameters is defined in run


"""
    



def run(filein, fileout, A, t, c, ultrasound=False, verbose=False):
    """
    Reads in filein, transforms the image based on pm, 
    and saves the file as fileout.
    :param filein: The input file path
    :param fileout: The output file path
    :param A: 3x3 numpy array consisting of a rotation matrix
    :param t: 1x3 numpy array consisting of the translational values
    :param c: Center of rotation. If none given, geometric center is used.
        If c=='origin', the origin is used
    :param ultrasound: Optional bool to be used if input image
        is an ultrasound or ultrasound slice
    :param verbose: Optional bool to control the amount of system logging
    :type filein: string
    :type fileout: string
    :type A: numpy.ndarray
    :type t: numpy.ndarray
    :type c: string or(int, int, int)
    :type ultrasound: bool
    :type verbose: bool
    :returns: None
    :rtype: NoneType


    """
    img = read_image(filein, ultrasound)
    pm = generate_affine_transform(img, A, t, c)
    out_img = transform(img, pm, verbose)
    write_image(out_img, fileout)
    

def read_image(path, ultrasound=False):
    """Load image from filepath as SimpleITK.Image

    :param path: Path to .nii file containing image.
    :param ultrasound: Optional. If True, image will be cast as sitkUInt16 for ultrasound images.
    :type path: str
    :type ultrasound: bool
    :returns: Image object from path
    :rtype: SimpleITK.Image
    """
    image = sitk.ReadImage(path)
    if ultrasound:
        image = sitk.Cast(image, sitk.sitkUInt16)
    return image


def write_image(image, path):
    """Write an image to file

    :param image: Image to be written
    :param path: Destination where image will be written to
    :type image: SimpleITK.Image
    :type path: str
    :rtype: None
    """
    sitk.WriteImage(image, path)


def transform(image, parameter_maps, verbose=False):
    """Transform an image according to some vector of parameter maps

    :param image: Image to be transformed
    :param parameter_maps: Vector of 3 parameter maps used to dictate the
                           image transformation
    :type image: SimpleITK.Image
    :type parameter_maps: [SimpleITK.ParameterMap]
    :returns: Transformed image
    :rtype: SimpleITK.Image
    """

    transform_filter = sitk.TransformixImageFilter()
    if not verbose:
        transform_filter.LogToConsoleOff()
    transform_filter.SetTransformParameterMap(parameter_maps)
    transform_filter.SetMovingImage(image)
    transform_filter.Execute()
    image = transform_filter.GetResultImage()
    return image

def generate_affine_transform(img, A, t, c):
    """Initializes an affine transform parameter map for a given image.

    The transform fits the following format: T(x) = A(x-c) + c + t

    :param img: Image to be transformed
    :param A: 3x3 numpy array consisting of a rotation matrix
    :param t: 1x3 numpy array consisting of the translational values
    :param c: Center of rotation. If none given, geometric center is used.
        If c=='origin', the origin is used
    :type img: SimpleITK.Image
    :type A: numpy.ndarray
    :type t: numpy.ndarray
    :type c: string or(int, int, int)
    :rtype: dict
    """
    affine = _get_default_affine_transform()

    f = lambda x: tuple([str(i) for i in x])
    affine['Size'] = f(img.GetSize())
    affine['Spacing'] = f(img.GetSpacing())
    affine['Origin'] = f(img.GetOrigin())
    affine['Direction'] = f(img.GetDirection())

    if c == 'origin':
        affine['CenterOfRotationPoint'] = affine['Origin']
    elif c:
        affine['CenterOfRotationPoint'] = f(c)
    else:
        offset = [.5*x*y for x, y in zip(img.GetSize(), img.GetSpacing())]
        affine['CenterOfRotationPoint'] = f([x + y for x, y in zip(offset, img.GetOrigin())])

    transform = np.concatenate((A, t), axis=0)

    affine['TransformParameters'] = f(transform.ravel())
    return affine


def _get_default_affine_transform():
    affine = {
    'AutomaticScalesEstimation': ('True'),
    'CenterOfRotationPoint': ('0.0', '0.0', '0.0'), 
    'CompressResultImage': ('false',), 
    'DefaultPixelValue': ('0.000000',), 
    'FinalBSplineInterpolationOrder': ('3',),
    'FixedInternalImagePixelType': ('float',), 
    'Index': ('0', '0', '0'), 
    'NumberOfParameters': ('12',),  
    'ResampleInterpolator': ['FinalNearestNeighborInterpolator'], 
    'Resampler': ('DefaultResampler',), 
    'ResultImageFormat': ('nii',), 
    'ResultImagePixelType': ('float',), 
    'Transform': ('AffineTransform',),
    'UseDirectionCosines': ('true',)
    }
    return affine


def perform_transforms(filename):
    workbook = xlrd.open_workbook(filename, on_demand=True)
    worksheet = workbook.sheet_by_index(0)
    if worksheet.cell(0,1).value == xlrd.empty_cell.value:
        ultrasound = True
    else:
        ultrasound = bool(worksheet.cell(0,1).value)
    if worksheet.cell(0,3).value == xlrd.empty_cell.value:
        verbose = False
    else:
        verbose = bool(worksheet.cell(0, 3).value)
    row = 2
    while row < worksheet.nrows and worksheet.cell(row, 0).value != xlrd.empty_cell.value:
        col = lambda c: worksheet.cell(row, c).value
        filein = col(0)
        fileout = col(1)
        A = np.array([[float(col(2)), float(col(3)), float(col(4))],
                    [float(col(5)), float(col(6)), float(col(7))],
                    [float(col(8)), float(col(9)), float(col(10))]])
        t = np.array([[float(col(11)), float(col(12)), float(col(13))]])
        if col(14).lower() == "none":
            c = None
        elif col(15).lower() == "origin":
            c = "origin"
        else:
            c = np.array([[float(col(14)), float(col(15)), float(col(16))]])
        row += 1

if __name__ == "__main__":
    if len(sys.argv) == 1:
        filein = "SAMPLE FILE IN" #ORIGINAL FILENAME HERE
        fileout = "SAMPLE FILE OUT" #NEW FILENAME HERE
        A = np.array([[1, 0, 0], #AFFINE MATRIX HERE 
                    [0, 1, 0],
                    [0, 0, 1]])

        t = np.array([[0, 0, 0]]) #TRANSLATION VECTOR HERE
        c = None # CENTER OF ROTATION HERE
        ultrasound = True #MARK TRUE ONLY IF USING ULTRASOUND FILES
        verbose = False #MARK TRUE FOR MORE TERMINAL OUTPUT

        run(filein, fileout, A, t, c, ultrasound, verbose)
    else:
        perform_transforms(sys.argv[1])



