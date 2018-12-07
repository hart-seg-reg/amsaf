
import numpy as np

import SimpleITK as sitk



    

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
    return DEFAULT_AFFINE

DEFAULT_AFFINE = {
    "AutomaticParameterEstimation": ['true'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid":
        ['FixedSmoothingImagePyramid', 'FixedRecursiveImagePyramid'],#first one
    "ImageSampler": ['RandomCoordinate'],
    "Interpolator": ['BSplineInterpolator'],#Linear Interpolator
    "MaximumNumberOfIterations": ['1024.000000'],#256
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],
    "NewSamplesEveryIteration": ['true'],
    "NumberOfHistogramBins": ['32.000000'],#nonexistant
    "NumberOfResolutions": ['4.000000'],
    "NumberOfSamplesForExactGradient": ['4096.000000'],
    "NumberOfSpatialSamples": ['2048.000000'],
    "Optimizer": ['AdaptiveStochasticGradientDescent'],
    "Registration": ['MultiResolutionRegistration'],
    "ResampleInterpolator": ['FinalBSplineInterpolator'],
    "Resampler": ['DefaultResampler'],
    "ResultImageFormat": ['nii'],
    "Transform": ['AffineTransform'],
    "WriteIterationInfo": ['false'],
    "WriteResultImage": ['true'],
}

if __name__ == "__main__":
    filein = "SAMPLE FILE IN"
    fileout = "SAMPLE FILE OUT"
    A = np.array([[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]])

    t = np.array([[0, 0, 0]])
    c = None
    ultrasound = True
    verbose = False

    run(filein, fileout, A, t, c, ultrasound, verbose)




