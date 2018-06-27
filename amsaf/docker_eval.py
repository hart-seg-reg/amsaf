import SimpleITK as sitk
import amsaf
import sys, time

def run_amsaf():
    directory = "/srv/mri_data/"
    unsegmented_image = amsaf.read_image(directory + "sub1_full.nii")

    ground_truth = amsaf.read_image(directory + "sub1_full_seg.nii")

    segmented_image = amsaf.read_image(directory + "sub2_full.nii")

    segmentation = amsaf.read_image(directory + "sub2_full_seg.nii")


    amsaf_results = amsaf.amsaf_eval(unsegmented_image, ground_truth, segmented_image, segmentation, get_param_maps(), verbose=True, memoize=False)
    amsaf.write_top_k(1, amsaf_results, '/home/chris/amsaf_results/mri_no_memo/')


def get_param_maps():
  rigid = {
    "AutomaticParameterEstimation": ['true'],
    "AutomaticTransformInitialization": ['true'],
    "BSplineInterpolationOrder": ['3.000000'],
    "CheckNumberOfSamples": ['true'],
    "DefaultPixelValue": ['0.000000'],
    "FinalBSplineInterpolationOrder": ['3.000000'],
    "FixedImagePyramid": ['FixedSmoothingImagePyramid'],
    "ImageSampler": ['RandomCoordinate'],
    "Interpolator": ['BSplineInterpolator'],
    "MaximumNumberOfIterations": ['1024.000000'],
    "MaximumNumberOfSamplingAttempts": ['8.000000'],
    "Metric": ['AdvancedMattesMutualInformation'],
    "MovingImagePyramid": ['MovingSmoothingImagePyramid'],
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
    "Transform": ['EulerTransform'],
    "WriteIterationInfo": ['false'],
    "WriteResultImage": ['true'],
  }
  affine = {
    "AutomaticParameterEstimation": ['true'],
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
    'Transform': ['BSplineTransform'],
    'WriteIterationInfo': ['false'],
    'WriteResultImage': ['true']
  }

  return [rigid, affine, bspline]



if __name__ == '__main__':
  start = time.time()
  run_amsaf()
  end = time.time()
  print("TIME:", end-start)
