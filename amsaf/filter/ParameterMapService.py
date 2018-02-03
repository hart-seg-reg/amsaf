import SimpleITK as sitk
from RigidParameterMapGenerator import RigidParameterMapGenerator
from AffineParameterMapGenerator import AffineParameterMapGenerator
from BSplineParameterMapGenerator import BSplineParameterMapGenerator


class ParameterMapService(object):
    def __init__(self, rigidParameterMapGeneratorInjectable=RigidParameterMapGenerator,
                 affineParameterMapGeneratorInjectable=AffineParameterMapGenerator,
                 bSplineParameterMapGeneratorInjectable=BSplineParameterMapGenerator):
        super(ParameterMapService, self).__init__()
        self.rigidParameterMapGenerator = rigidParameterMapGeneratorInjectable()
        self.affineParameterMapGenerator = affineParameterMapGeneratorInjectable()
        self.bSplineParameterMapGenerator = bSplineParameterMapGeneratorInjectable()

    def addParameterPriors(self, parameterPriors):
        if parameterPriors['rigid']:
            self.rigidParameterMapGenerator.addParameterPriors(parameterPriors['rigid'])
        if parameterPriors['affine']:
            self.affineParameterMapGenerator.addParameterPriors(parameterPriors['affine'])
        if parameterPriors['bSpline']:
            self.bSplineParameterMapGenerator.addParameterPriors(parameterPriors['bSpline'])

    def generateParameterMaps(self):
        # type: ([dict]) -> [sitk.ParameterMap, sitk.ParameterMap, sitk.ParameterMap]

        for rigidPM in self.rigidParameterMapGenerator.generateParameterMaps():
            for affinePM in self.affineParameterMapGenerator.generateParameterMaps():
                for bSplinePM in self.bSplineParameterMapGenerator.generateParameterMaps():
                    yield [rigidPM, affinePM, bSplinePM]
