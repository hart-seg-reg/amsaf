from sklearn.model_selection import ParameterGrid
import SimpleITK as sitk


class ParameterMapGenerator(object):
    def __init__(self):
        super(ParameterMapGenerator, self).__init__()
        self._transformType = None
        self._paramDict = {}

    #######################
    # Getters and Setters #
    #######################

    @property
    def transformType(self):
        return self._transformType

    @transformType.setter
    def transformType(self, value):
        self._transformType = value

    @property
    def paramDict(self):
        return self._paramDict

    @paramDict.setter
    def paramDict(self, value):
        self._paramDict = value

    ###########
    # Methods #
    ###########

    def addParameterPriors(self, parameterPriors):
        # type: (dict) -> None
        for gridParam, _ in self.paramDict.iteritems():
            for priorParam, priorValue in parameterPriors.iteritems():
                if gridParam == priorParam:
                    self.paramDict[gridParam] = priorValue

    def _convertToElastix(self, parameterGridItem):
        # type: (dict) -> sitk.ParameterMap
        elastixParameterMap = sitk.GetDefaultParameterMap(self.transformType)

        for param, value in parameterGridItem.iteritems():
            elastixParameterMap[param] = [value]

        return elastixParameterMap

    def generateParameterMaps(self):
        # type: () -> sitk.ParameterMap
        parameterGrid = ParameterGrid(self.paramDict)

        for elem in parameterGrid:
            yield self._convertToElastix(elem)
