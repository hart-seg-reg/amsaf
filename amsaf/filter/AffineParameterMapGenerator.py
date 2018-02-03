from ParameterMapGenerator import ParameterMapGenerator


class AffineParameterMapGenerator(ParameterMapGenerator):
    def __init__(self):
        super(AffineParameterMapGenerator, self).__init__()
        self.transformType = 'affine'
        self.paramDict = {
            "AutomaticParameterEstimation": ['true'],
            "CheckNumberOfSamples": ['true'],
            "DefaultPixelValue": ['0.000000'],
            "FinalBSplineInterpolationOrder": ['3.000000'],
            "FixedImagePyramid": ['FixedSmoothingImagePyramid', 'FixedRecursiveImagePyramid'],
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
