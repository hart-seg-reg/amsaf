import SimpleITK as sitk


class MockParameterMapService(object):
    def __init__(self):
        super(MockParameterMapService, self).__init__()

    @staticmethod
    def generateParameterMaps():
        rigidMap = sitk.GetDefaultParameterMap('rigid')
        rigidMap['AutomaticTransformInitialization'] = ['true']
        affineMap = sitk.GetDefaultParameterMap('affine')
        bSplineMap = sitk.GetDefaultParameterMap('bspline')

        yield [rigidMap, affineMap, bSplineMap]
