from ParameterMapGenerator import ParameterMapGenerator


class RigidParameterMapGenerator(ParameterMapGenerator):
    def __init__(self):
        super(RigidParameterMapGenerator, self).__init__()
        self.transformType = 'rigid'
        self.paramDict = {
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
