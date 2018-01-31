"""A functional implementation of AMSAF"""
"""
Notes:
Public functionality should include:
  * Given a mapping or tuple of image files and optional parameter maps, run a
    single instance of Elastix/Transformix registration + transformation and
    return the transformed image and associated parameter map.
  * Given a mapping or tuple of image files, optional parameter map priors, and
    optional similarity metrics run an instance of AMSAF and return a lazy
    generator representing the set of 3-tuple (score, parameter map, image)
    results.
  * Given a generator of AMSAF results and an integer N, return the N best
    results
  * Given a generator of AMSAF results and an integer N, write the N best
    results
  * Other assorted utility functions for working with results in an easy way
"""

import SimpleITK as sitk
from sklearn.model_selection import ParameterGrid
import cytoolz as ct


def amsaf_rank(unsegmented_image,
               segmented_image,
               unsegmented_image_gt,
               segmented_image_gt,
               parameter_priors=None):
    default_rigid = {
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

    default_affine = {
        "AutomaticParameterEstimation": ['true'],
        "CheckNumberOfSamples": ['true'],
        "DefaultPixelValue": ['0.000000'],
        "FinalBSplineInterpolationOrder": ['3.000000'],
        "FixedImagePyramid":
        ['FixedSmoothingImagePyramid', 'FixedRecursiveImagePyramid'],
        "ImageSampler": ['RandomCoordinate'],
        "Interpolator": ['BSplineInterpolator'],
        "MaximumNumberOfIterations": ['1024.000000'],
        "MaximumNumberOfSamplingAttempts": ['8.000000'],
        "Metric": ['AdvancedMattesMutualInformation'],
        "MovingImagePyramid": ['MovingSmoothingImagePyramid'],
        "NewSamplesEveryIteration": ['true'],
        "NumberOfHistogramBins": ['32.000000'],
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

    default_bspline = {
        'AutomaticParameterEstimation': ["true"],
        'CheckNumberOfSamples': ["true"],
        'DefaultPixelValue': ['0.000000'],
        'FinalBSplineInterpolationOrder': ['3.000000'],
        'FinalGridSpacingInPhysicalUnits': ['4.000000', '6.000000'],
        'FixedImagePyramid': ['FixedSmoothingImagePyramid'],
        'ImageSampler': ['RandomCoordinate'],
        'Interpolator': ['LinearInterpolator'],
        'MaximumNumberOfIterations': ['1024.000000'],
        'MaximumNumberOfSamplingAttempts': ['8.000000'],
        'Metric':
        ['AdvancedMattesMutualInformation', 'TransformBendingEnergyPenalty'],
        'Metric0Weight': ['0', '0.5', '1.000000', '2.0'],
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

    pm_gen = ct.mapcat(param_combinations,
                       [(default_rigid, 'rigid'), (default_affine, 'affine'),
                        (default_bspline, 'bspline')])

    segf = ct.partial(segment, unsegmented_image, segmented_image,
                      segmented_image_gt)

    return ct.map(segf, pm_gen)


def format_result(parameter_map, ground_truth, candidate):
    return [parameter_map, candidate, sim_score(candidate, ground_truth)]


def param_combinations(param_options):
    option_dict, transform_type = param_options
    return (to_elastix(pm, transform_type)
            for pm in ParameterGrid(option_dict))


def to_elastix(pm, ttype):
    elastix_pm = sitk.GetDefaultParameterMap(ttype)
    for k, v in pm.iteritems():
        elastix_pm[k] = [v]
    return elastix_pm


def sim_score(candidate, ground_truth):
    overlap_filter = sitk.LabelOverlapMeasuresImageFilter()
    overlap_filter.Execute(ground_truth, candidate)
    return overlap_filter.GetDiceCoefficient()


def segment(unsegmented_image,
            segmented_image,
            segmentation,
            parameter_maps=None):
    moving_image = sitk.ReadImage(segmented_image)
    fixed_image = sitk.ReadImage(unsegmented_image)
    _, transform_parameter_maps = register(fixed_image, moving_image,
                                           parameter_maps)

    return transform(segmentation, nn_assoc(transform_parameter_maps))


def nn_assoc(pms):
    return pm_vec_assoc('ResampleInterpolator',
                        'FinalNearestNeighborInterpolator', pms)


def auto_init_assoc(pms):
    return pm_vec_assoc('AutomaticTransformInitialization', 'true', pms)


@ct.curry
def pm_assoc(k, v, pm):
    return ct.update_in(pm, [k], lambda _: [v])


def pm_vec_assoc(k, v, pms):
    return list(ct.map(pm_assoc(k, v), pms))


def register(fixed_image,
             moving_image,
             parameter_maps=None,
             auto_init=True,
             verbose=False):
    registration_filter = sitk.ElastixImageFilter()
    if not verbose:
        registration_filter.LogToConsoleOff()
    registration_filter.SetFixedImage(fixed_image)
    registration_filter.SetMovingImage(moving_image)

    if parameter_maps:
        if auto_init:
            parameter_maps = auto_init_assoc(parameter_maps)
        registration_filter.SetParameterMap(parameter_maps[0])
        for m in parameter_maps[1:]:
            registration_filter.AddParameterMap(m)

    registration_filter.Execute()
    result_image = registration_filter.GetResultImage()
    transform_parameter_maps = registration_filter.GetTransformParameterMap()

    return result_image, transform_parameter_maps


def transform(image, parameter_maps, verbose=False):
    transform_filter = sitk.TransformixImageFilter()
    if not verbose:
        transform_filter.LogToConsoleOff()
    transform_filter.SetTransformParameterMap(parameter_maps)
    transform_filter.SetMovingImage(image)
    transform_filter.Execute()
    result_image = transform_filter.GetResultImage()

    return result_image
