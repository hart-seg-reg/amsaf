# -*- coding: utf-8 -*-

"""
.. module:: amsaf
   :synopsis: A functional(ish) implementation of AMSAF

AMSAF is comprised of several utility functions which wrap SimpleITK and Elastix
to facilitate easy registration, transformation, and segmentation
of .nii images. It's core functionality, amsaf_eval,
allows for quicker development of Elastix parameter maps by generating and
ranking the results of parameter map instances in a caller-defined search space.
"""

import os
import glob

import SimpleITK as sitk
from sklearn.model_selection import ParameterGrid


###########################
# Public module functions #
###########################


def amsaf_eval(unsegmented_image,
               ground_truth,
               segmented_image,
               segmentation,
               parameter_priors=None,
               verbose=False, 
               memoize=False):
    """Main AMSAF functionality

    Generate and score new segmentations and corresponding Elastix parameter
    maps.

    :param unsegmented_image: The target for segmentation and scoring.
    :param ground_truth: The segmentation slice of unsegmented_image used as a
                         ground truth to score images generated by AMSAF.
    :param segmented_image: The image we want to map a segmentation from.
    :param segmentation: The segmentation corresponding to segmented_image.
    :param parameter_priors: An optional vector of 3 ParameterGrid-style dicts
                             mapping Elastix parameter map keys to lists of
                             values. Each value list will be substituted
                             in for the corresponding key in a default dict
                             so that the caller can specify specific
                             combinations of values for some keys, usually to
                             constrain the search space for testing or time
                             consideration.
    :param verbose: Optional boolean flag to toggle verbose stdout printing from
                    Elastix.
    :param memoize: Optional boolean flag to toggle memoization optimization
    :type unsegmented_image: SimpleITK.Image
    :type ground_truth: SimpleITK.Image
    :type segmented_image: SimpleITK.Image
    :type segmentation: SimpleITK.Image
    :type parameter_priors: dict
    :type verbose: bool
    :type memoize: bool
    :returns: A lazy stream of result
              (parameter map vector, result segmentation, segmentation score) lists.
    :rtype: generator
    """

    def eval_pm(parameter_map):
        seg = segment(
            unsegmented_image,
            segmented_image,
            segmentation,
            parameter_map,
            verbose=verbose)
        if ground_truth is not None:
            score = _sim_score(seg, ground_truth)
        else: 
            score = 0
        return [parameter_map, seg, score]

    def param_combinations(option_dict, transform_type):
        return (_to_elastix(pm, transform_type)
                for pm in ParameterGrid(option_dict))

    if not parameter_priors:
        parameter_priors = _get_default_vector()

    if memoize:
        for rpm in param_combinations(parameter_priors[0], 'rigid'):
            translation_image, translation_pm = register_indv(unsegmented_image, segmented_image, 'translation', rpm, verbose=verbose)
            for apm in param_combinations(parameter_priors[1], 'affine'):
                affine_image, affine_pm = register_indv(translation_image, segmented_image, 'affine', apm, verbose=verbose)
                for bpm in param_combinations(parameter_priors[2], 'bspline'):
                    bspline_image, bspline_pm = register_indv(bspline_image, segmented_image, bpm, 'bspline', verbose=verbose)
                    transform_parameter_maps = [rpm, apm, bpm]
                    transformed_seg = transform(segmentation, _nn_assoc(transform_parameter_maps), verbose=verbose)
                    if ground_truth is not None:
                        score = _sim_score(bspline_image, ground_truth)
                    else:
                        score = 0
                    yield [ transform_parameter_maps , transformed_seg, score]

    else:
        for rpm in param_combinations(parameter_priors[0], 'rigid'):
            for apm in param_combinations(parameter_priors[1], 'affine'):
                for bpm in param_combinations(parameter_priors[2], 'bspline'):
                    yield eval_pm([rpm, apm, bpm])


def write_top_k(k, amsaf_results, path):
    """Write top k results to filepath

    Results are written as subdirectories "result-i" for 0 < i <= k.
    Each subdirectory contains the result's corresponding parameter maps,
    segmentation, and score.

    :param k: Number of results to write
    :param amsaf_results: Results in the format of amsaf_eval return value
    :param path: Filepath to write results at
    :type: k: int
    :type amsaf_result: [[SimpleITK.ParameterMap, SimpleITK.Image, float]]
    :type path: str
    :rtype: None
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    for i, result in enumerate(top_k(k, amsaf_results)):
        write_result(result, os.path.join(path, 'result-{}'.format(i)))


def register(fixed_image,
             moving_image,
             parameter_maps=None,
             auto_init=True,
             verbose=False):
    """Register images using Elastix.

    :param parameter_maps: Optional vector of 3 parameter maps to be used for
                           registration. If none are provided, a default vector
                           of [rigid, affine, bspline] parameter maps is used.
    :param auto_init: Auto-initialize images. This helps with flexibility when
                      using images with little overlap.
    :param verbose: Flag to toggle stdout printing from Elastix
    :type fixed_image: SimpleITK.Image
    :type moving_image: SimpleITK.Image
    :type parameter_maps: [SimpleITK.ParameterMap]
    :type auto_init: bool
    :type verbose: bool
    :returns: Tuple of (result_image, transform_parameter_maps)
    :rtype: (SimpleITK.Image, [SimpleITK.ParameterMap])
    """
    registration_filter = sitk.ElastixImageFilter()
    if not verbose:
        registration_filter.LogToConsoleOff()
    registration_filter.SetFixedImage(fixed_image)
    registration_filter.SetMovingImage(moving_image)

    if not parameter_maps:
        parameter_maps = _get_default_vector()
    if auto_init:
        parameter_maps = _auto_init_assoc(parameter_maps)
    registration_filter.SetParameterMap(parameter_maps[0])
    for m in parameter_maps[1:]:
        registration_filter.AddParameterMap(m)

    registration_filter.Execute()
    result_image = registration_filter.GetResultImage()
    transform_parameter_maps = registration_filter.GetTransformParameterMap()

    return result_image, transform_parameter_maps

def register_indv(fixed_image,
             moving_image,
             transform_type,
             parameter_map=None,
             auto_init=True,
             verbose=False):
    """Register images using Elastix. Used to perform transforms individually
        Namely used for memoization to avoid redundant computation

    :param transform_type: Type of tranform to be performed
    :type transform_type: String
    :param parameter_map: Optional parameter map to be used for
                           registration. If none is provided, a default map based on transform type is used.
    :param auto_init: Auto-initialize images. This helps with flexibility when
                      using images with little overlap.
    :param verbose: Flag to toggle stdout printing from Elastix
    :type fixed_image: SimpleITK.Image
    :type moving_image: SimpleITK.Image
    :type parameter_map: SimpleITK.ParameterMap
    :type auto_init: bool
    :type verbose: bool
    :returns: Tuple of (result_image, transform_parameter_maps)
    :rtype: (SimpleITK.Image, [SimpleITK.ParameterMap])
    """
    registration_filter = sitk.ElastixImageFilter()
    if not verbose:
        registration_filter.LogToConsoleOff()
    registration_filter.SetFixedImage(fixed_image)
    registration_filter.SetMovingImage(moving_image)

    if not parameter_map:
        if transform_type == 'rigid':
            parameter_map = _get_default_rigid()
        elif transform_type == 'affine':
            parameter_map = _get_default_affine()
        elif transform_type == 'bspline':
            parameter_map = _get_default_bspline()
        
    if auto_init: #Make sure still works later
        parameter_map = _auto_init_assoc(parameter_maps)
    registration_filter.SetParameterMap(parameter_map)

    registration_filter.Execute()
    result_image = registration_filter.GetResultImage()
    transform_parameter_maps = registration_filter.GetTransformParameterMap()

    return result_image, transform_parameter_map



def segment(unsegmented_image,
            segmented_image,
            segmentation,
            parameter_maps=None,
            verbose=False):
    """Segment image using Elastix

    :param segmented_image: Image with corresponding segmentation passed as
                            the next argument
    :param segmentation: Segmentation to be mapped from segmented_image to
                         unsegmented_image
    :param parameter_maps: Optional vector of 3 parameter maps to be used for
                           registration. If none are provided, a default vector
                           of [rigid, affine, bspline] parameter maps is used.
    :param verbose: Flag to toggle stdout printing from Elastix
    :type unsegmented_image: SimpleITK.Image
    :type segmented_image: SimpleITK.Image
    :type segmentation: SimpleITK.Image
    :type parameter_maps: [SimpleITK.ParameterMap]
    :type verbose: bool
    :returns: Segmentation mapped from segmented_image to unsegmented_image
    :rtype: SimpleITK.Image
    """
    _, transform_parameter_maps = register(
        unsegmented_image, segmented_image, parameter_maps, verbose=verbose)

    return transform(
        segmentation, _nn_assoc(transform_parameter_maps), verbose=verbose)



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
    result_image = transform_filter.GetResultImage()

    return result_image


def read_image(path, ultrasound_slice=False):
    """Load image from filepath as SimpleITK.Image

    :param path: Path to .nii file containing image.
    :param ultrasound_slice: Optional. If True, image will be cast as sitkUInt16 for ultrasound images.
    :type path: str
    :returns: Image object from path
    :rtype: SimpleITK.Image
    """
    image = sitk.ReadImage(path)
    if ultrasound_slice:
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


def write_result(amsaf_result, path):
    """Write single amsaf_eval result to path

    Writes parameter maps, segmentation, and score of AMSAF result as individual
    files at path.

    :param amsaf_results: Results in the format of amsaf_eval return value
    :param path: Filepath to write results at
    :type amsaf_result: [SimpleITK.ParameterMap, SimpleITK.Image, float]
    :type path: str
    :rtype: None
    """
    if not os.path.isdir(path):
        os.makedirs(path)
    for i, pf in enumerate(amsaf_result[0]):
        sitk.WriteParameterFile(pf,
                                os.path.join(
                                    path, 'parameter-file-{}.txt'.format(i)))

    sitk.WriteImage(amsaf_result[1], os.path.join(path, 'seg.nii'))

    with open(os.path.join(path, 'score.txt'), 'w') as f:
        f.write('{}\n'.format(amsaf_result[2]))


def top_k(k, amsaf_results):
    """Get top k results of amsaf_eval

    :param k: Number of results to return. If k == 0, returns all results
    :param amsaf_results: Results in the format of amsaf_eval return value
    :type k: int
    :type amsaf_result: [[SimpleITK.ParameterMap, SimpleITK.Image, float]]
    :returns: Top k result groups ordered by score
    :rtype: [[SimpleITK.ParameterMap, SimpleITK.Image, float]]
    """
    if k == 0:
        sorted(amsaf_results, key=lambda x: x[-1], reverse=True)
    return sorted(amsaf_results, key=lambda x: x[-1], reverse=True)[:k]


def seg_map(segmented_subject_dir, unsegmented_subject_dir, segmentation_dir, filenames, parameter_maps=None,
            strict=False):
    """Intra-subject segmentation mappings from supplied filenames

    :param segmented_subject_dir: Directory with data of segmented image
    :param unsegmented_subject_dir: Directory with data of unsegmented_image
    :param segmentation_dir: Directory with data of segmented image segmentation
    :param filenames: Iterable of filenames to map
    :param parameter_maps: Optional vector of 3 parameter maps to be used for
                           registration. If none are provided, a default vector
                           of [rigid, affine, bspline] parameter maps is used.
    :param strict: Default False. If True, a ValueError will be raised when some filename is not present in every
                   supplied directory.

    :rtype: [SimpleITK.Image]

    >>> us_data = os.path.join(os.path.sep, 'srv', 'ultrasound_data')
    >>> sub1 = os.path.join(us_data, 'sub1')
    >>> sub2 = os.path.join(us_data, 'sub2')
    >>> sub1_trials = os.path.join(sub1, 'trials')
    >>> sub2_trials = os.path.join(sub2, 'trials')
    >>> sub1_seg = os.path.join(sub1, seg)
    >>> sub2_hand_shoulder_seg = seg_map(sub1_trials, sub2_trials, sub1_seg, ['trial18_90_fs_volume.mha'])
    """
    result_segs = []
    for f in filenames:
        unsegmented_image = os.path.join(unsegmented_subject_dir, f)
        segmented_image = os.path.join(segmented_subject_dir, f)
        segmentation = os.path.join(segmentation_dir, f)

        if not all([os.path.isfile(image) for image in [unsegmented_image, segmented_image, segmentation]]):
            if strict:
                raise ValueError("File {} is not in all supplied directories".format(f))
            continue

        result_segs.append(segment(unsegmented_image, segmented_image, segmentation, parameter_maps=parameter_maps))

    return result_segs


def seg_map_all(segmented_subject_dir, unsegmented_subject_dir, segmentation_dir,
                parameter_maps=None, image_type='volume', strict=False):
    """Intra-subject segmentation mappings

    Like seg_map, but selects all files of image_type in supplied directories as filename selection.

    :param segmented_subject_dir: Directory with data of segmented image
    :param unsegmented_subject_dir: Directory with data of unsegmented_image
    :param segmentation_dir: Directory with data of segmented image segmentation
    :param parameter_maps: Optional vector of 3 parameter maps to be used for
                           registration. If none are provided, a default vector
                           of [rigid, affine, bspline] parameter maps is used.
    :param image_type: Either 'volume' or 'slice' corresponding to extensions '.mha' or '.nii', respectively
    :param strict: Default False. If True, a ValueError will be raised when some filename is not present in every
                   supplied directory.

    :rtype: [SimpleITK.Image]

    >>> us_data = os.path.join(os.path.sep, 'srv', 'ultrasound_data')
    >>> sub1 = os.path.join(us_data, 'sub1')
    >>> sub2 = os.path.join(us_data, 'sub2')
    >>> sub1_trials = os.path.join(sub1, 'trials')
    >>> sub2_trials = os.path.join(sub2, 'trials')
    >>> sub1_seg = os.path.join(sub1, seg)
    >>> sub2_segs = seg_map_all(sub1_trials, sub2_trials, sub1_seg)
    """
    sub1_images = _image_set(segmented_subject_dir, image_type=image_type)
    sub2_images = _image_set(unsegmented_subject_dir, image_type=image_type)

    matches = sub1_images.intersection(sub2_images)
    return seg_map(segmented_subject_dir, unsegmented_subject_dir, segmentation_dir, matches,
                   parameter_maps=parameter_maps, strict=strict)


##########################
# Private module helpers #
##########################

def _image_set(dirname, image_type='volume'):
    if image_type == 'volume':
        ext = '.mha'
    elif image_type == 'slice':
        ext = '.nii'
    else:
        raise ValueError("kwarg image_type must be either 'volume' or 'slice'")
    images = glob.glob(os.path.join(dirname, '*{}'.format(ext)))
    return set(os.path.basename(image) for image in images)


def _to_elastix(pm, ttype):
    elastix_pm = _get_default_vector()
    for k, v in pm.iteritems():
        if type(v) == list:
            elastix_pm[k] = v
        else:
            elastix_pm[k] = [v]
    return elastix_pm


def _sim_score(candidate, ground_truth):
    candidate = sitk.Cast(candidate, ground_truth.GetPixelID())
    candidate.CopyInformation(ground_truth)

    overlap_filter = sitk.LabelOverlapMeasuresImageFilter()
    overlap_filter.Execute(ground_truth, candidate)
    return overlap_filter.GetDiceCoefficient()


def _nn_assoc(pms):
    return _pm_vec_assoc('ResampleInterpolator',
                         'FinalNearestNeighborInterpolator', pms)


def _auto_init_assoc(pms):
    return _pm_vec_assoc('AutomaticTransformInitialization', 'true', pms)


def _pm_assoc(k, v, pm):
    result = {}
    for key, val in pm.iteritems():
        if key == k:
            result[key] = [v]
        else:
            result[key] = val
    return result


def _pm_vec_assoc(k, v, pms):
    return [_pm_assoc(k, v, pm) for pm in pms]


def _get_default_rigid():
    return DEFAULT_RIGID


def _get_default_affine():
    return DEFAULT_AFFINE


def _get_default_bspline():
    return DEFAULT_BSPLINE


def _get_default_vector():
    return [_get_default_rigid(), _get_default_affine(), _get_default_bspline()]


##########################
# Default parameter maps #
##########################

# These should probably be moved to their own module if we add many more.
# If you do this, be sure to change the above helper functions.

DEFAULT_RIGID = {
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

DEFAULT_AFFINE = {
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

DEFAULT_BSPLINE = {
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
        [['AdvancedMattesMutualInformation', 'TransformBendingEnergyPenalty']],
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
