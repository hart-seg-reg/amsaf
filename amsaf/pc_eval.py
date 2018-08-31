import time

import SimpleITK as sitk

import amsaf
import numpy as np



def run_amsaf():
    verbose = True
    dir1 = "/Users/chris/Desktop/HART/ultrasound_data/"
    dir2 = "/Users/chris/Desktop/HART/ultrasound_data/Sub2/unprocessed/"
    dirB = "/Users/chris/Desktop/HART/ultrasound_data/SubB/"
    sb = "/Users/chris/Desktop/HART/ultrasound_data/sandbox/"
    unsegmented_image = amsaf.read_image(dirB + "subB_90_p5_volume.nii", True)
    ground_truth = None #amsaf.read_image(directory + "sub1_30_fs_seg_crop1.nii", True)
    segmented_image = amsaf.read_image(dirB + "subB_30_fs_volume.nii", True)
    segmentation = amsaf.read_image(dir1 + "subB_30_fs_seg.nii", True)

    #segmentation = amsaf.transform(segmentation, get_rotation(segmentation), verbose)
    #segmented_image = amsaf.transform(segmented_image, get_rotation(segmented_image), verbose)

    #segmentation = amsaf.transform(segmentation, get_init_transform(segmentation), verbose)
    #segmented_image = amsaf.transform(segmented_image, get_init_transform(segmented_image), verbose)



    amsaf_results = amsaf.amsaf_eval(unsegmented_image, ground_truth, segmented_image, segmentation, get_param_maps(), verbose=verbose)
    amsaf.write_top_k(10, amsaf_results, 'subB_30_fs_to_90_p5')

def transform():
    verbose = False
    img_dir = "/Users/chris/Desktop/HART/ultrasound_data/Sub1/croppings/"
    out_dir = img_dir
    sb = "/Users/chris/Desktop/HART/ultrasound_data/sandbox/"
    f = img_dir + "sub1_30_fs_volume_crop1.nii"
    img = amsaf.read_image(f, True)
    print(img.GetSize(), img.GetOrigin())

    out_img = amsaf.transform(img, get_rotation(img), verbose)
    amsaf.write_image(out_img, sb + "sub1_30_fs_volume_cu_rot.nii")
    print(out_img.GetSize(), out_img.GetOrigin())


def get_param_maps():
  rigid = {
    "AutomaticParameterEstimation": ['true'],
    "AutomaticTransformInitialization": ['true'],
    "BSplineInterpolationOrder": ['3.000000'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid": ['FixedSmoothingImagePyramid'],#, 'FixedRecursiveImagePyramid'],
    "ImageSampler": ['RandomCoordinate'],
    "Interpolator": ['BSplineInterpolator'],
    "MaximumNumberOfIterations": ['1024.000000'],
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],#, 'MovingRecursiveImagePyramid'],
    "NewSamplesEveryIteration": ['true'],
    "NumberOfHistogramBins": ['64.000000'],
    "NumberOfResolutions": ['3.000000'],
    "NumberOfSamplesForExactGradient": ['4096.000000'],
    "NumberOfSpatialSamples": ['2000.000000'],
    "Optimizer": ['AdaptiveStochasticGradientDescent'],
    "Registration": ['MultiResolutionRegistration'],
    "ResampleInterpolator": ['FinalBSplineInterpolator'],
    "Resampler": ['DefaultResampler'],
    "ResultImageFormat": ['nii'],
    "RequiredRatioOfValidSamples": ['0.05'], 
    #"Scales": ['Float'],
    "Transform": ['EulerTransform'],
    "WriteIterationInfo": ['false'],
    "WriteResultImage": ['true'],
  }
  affine = {
    "AutomaticParameterEstimation": ['true'],
    "AutomaticScalesEstimation": ['true'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid":
        ['FixedSmoothingImagePyramid'],
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
    "RequiredRatioOfValidSamples": ['0.05'],
    "Transform": ['AffineTransform'],
    "WriteIterationInfo": ['false'],
    "WriteResultImage": ['true'],
  }
  bspline = {
    'AutomaticParameterEstimation': ["true"],
    'CheckNumberOfSamples': ["true"],
    'DefaultPixelValue': ['0.000000'],
    'FinalBSplineInterpolationOrder': ['3.000000'],
    'FinalGridSpacingInPhysicalUnits': ['4.000000'],
    'FixedImagePyramid': ['FixedSmoothingImagePyramid'],
    'GridSpaceSchedule': ['2.803220 1.988100 1.410000 1.000000'],
    'ImageSampler': ['RandomCoordinate'],
    'Interpolator': ['LinearInterpolator'],
    'MaximumNumberOfIterations': ['1024.000000'],
    'MaximumNumberOfSamplingAttempts': ['8.000000'],
    'Metric': ['AdvancedMattesMutualInformation'],
    'Metric0Weight': ['0'],
    'Metric1Weight': ['1.000000'],
    'MovingImagePyramid': ["MovingSmoothingImagePyramid"],
    'NewSamplesEveryIteration': ['true'],
    'NumberOfHistogramBins': ['32.000000'],
    'NumberOfResolutions': ['4.000000'],
    'NumberOfSamplesForExactGradient': ['4096.000000'],
    'NumberOfSpatialSamples': ['2048.000000'],
    'Optimizer': ['AdaptiveStochasticGradientDescent'],
    'Registration': ['MultiMetricMultiResolutionRegistration'],
    'ResampleInterpolator': ['FinalBSplineInterpolator'],
    'Resampler': ['DefaultResampler'],
    'ResultImageFormat': ['nii'],
    "RequiredRatioOfValidSamples": ['0.05'],
    'Transform': ['BSplineTransform'],
    'WriteIterationInfo': ['false'],
    'WriteResultImage': ['true']
  }

  return [rigid, affine, bspline]


def get_init_transform(img):
    affine = _get_default_affine()

    f = lambda x: tuple([str(i) for i in x])
    affine['Size'] = f(img.GetSize())
    affine['Spacing'] = f(img.GetSpacing())
    affine['Origin'] = f(img.GetOrigin())
    affine['Direction'] = f(img.GetDirection())
    affine['CenterOfRotationPoint'] = affine['Origin']

    offset = [.5*x*y for x, y in zip(img.GetSize(), img.GetSpacing())]
    affine['CenterOfRotationPoint'] = f([x + y for x, y in zip(offset, img.GetOrigin())])


    tp = np.array([[.91, .41, 0.04],
                    [-.41, .91, -.07], 
                    [-.05, 0.0, 1.0],
                    [0.0, 0.0, 0.0]])


    affine['TransformParameters'] = f(tp.ravel())
    return affine

def get_rotation(img):
    affine = _get_default_affine()

    f = lambda x: tuple([str(i) for i in x])
    affine['Size'] = f(img.GetSize())
    affine['Spacing'] = f(img.GetSpacing())
    affine['Origin'] = f(img.GetOrigin())
    affine['Direction'] = f(img.GetDirection())
    affine['CenterOfRotationPoint'] = affine['Origin']

    offset = [.5*x*y for x, y in zip(img.GetSize(), img.GetSpacing())]
    affine['CenterOfRotationPoint'] = f([x + y for x, y in zip(offset, img.GetOrigin())])


    tp = np.array([[0.0, 0.0, -1.0],
                    [0.0, -1.0, 0.0], 
                    [1.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0]])


    affine['TransformParameters'] = f(tp.ravel())
    return affine


def _get_default_affine():
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



if __name__ == '__main__':
  start = time.time()
  run_amsaf()
  #transform()
  end = time.time()
  print("TIME:" + str(end-start))
