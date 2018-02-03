from ParameterMapGenerator import ParameterMapGenerator


class BSplineParameterMapGenerator(ParameterMapGenerator):
    def __init__(self):
        super(BSplineParameterMapGenerator, self).__init__()
        self.transformType = 'bspline'
        self.paramDict = {
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
            'Metric': ['AdvancedMattesMutualInformation', 'TransformBendingEnergyPenalty'],
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
