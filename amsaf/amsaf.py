"""A functional(ish) implementation of AMSAF"""

import os
import heapq

import SimpleITK as sitk
from sklearn.model_selection import ParameterGrid

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


def amsaf_rank(unsegmented_image,
               segmented_image,
               unsegmented_image_gt,
               segmented_image_gt,
               parameter_priors=None,
               verbose=False):
    def eval_pm(parameter_map):
        seg = segment(
            unsegmented_image,
            segmented_image,
            segmented_image_gt,
            parameter_map,
            verbose=verbose)
        score = sim_score(seg, unsegmented_image_gt)
        return [parameter_map, seg, score]

    for rpm in param_combinations([default_rigid, 'rigid']):
        for apm in param_combinations([default_affine, 'affine']):
            for bpm in param_combinations([default_bspline, 'bspline']):
                yield eval_pm([rpm, apm, bpm])


def top_k(k, amsaf_results):
    return heapq.nlargest(k, amsaf_results, key=lambda x: x[-1])


def write_top_k(k, amsaf_results, path):
    if not os.path.isdir(path):
        os.makedirs(path)
    for i, result in enumerate(top_k(k, amsaf_results)):
        write_result(result, os.path.join(path, 'result-{}'.format(i)))


def write_result(amsaf_result, path):
    if not os.path.isdir(path):
        os.makedirs(path)
    for i, pf in enumerate(amsaf_result[0]):
        sitk.WriteParameterFile(pf,
                                os.path.join(
                                    path, 'parameter-file-{}.txt'.format(i)))

    sitk.WriteImage(amsaf_result[1], os.path.join(path, 'seg.nii'))

    with open(os.path.join(path, 'score.txt'), 'w') as f:
        f.write(str(amsaf_result[2]))


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
    candidate = sitk.Cast(candidate, ground_truth.GetPixelID())
    candidate.CopyInformation(ground_truth)

    overlap_filter = sitk.LabelOverlapMeasuresImageFilter()
    overlap_filter.Execute(ground_truth, candidate)
    return overlap_filter.GetDiceCoefficient()


def read_image(img):
    return sitk.ReadImage(img)


def segment(unsegmented_image,
            segmented_image,
            segmentation,
            parameter_maps=None,
            verbose=False):

    _, transform_parameter_maps = register(
        unsegmented_image, segmented_image, parameter_maps, verbose=verbose)

    return transform(
        segmentation, nn_assoc(transform_parameter_maps), verbose=verbose)


def nn_assoc(pms):
    return pm_vec_assoc('ResampleInterpolator',
                        'FinalNearestNeighborInterpolator', pms)


def auto_init_assoc(pms):
    return pm_vec_assoc('AutomaticTransformInitialization', 'true', pms)


def pm_assoc(k, v, pm):
    result = {}
    for key, val in pm.iteritems():
        if key == k:
            result[key] = [v]
        else:
            result[key] = val
    return result


def pm_vec_assoc(k, v, pms):
    return [pm_assoc(k, v, pm) for pm in pms]


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

    if not parameter_maps:
        parameter_maps = [
            sitk.GetDefaultParameterMap(t)
            for t in ['translation', 'affine', 'bspline']
        ]
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
