import heapq
import SimpleITK as sitk

from ParameterMapService import ParameterMapService


class AmsafExecutor(object):
    def __init__(self, parameterMapServiceInjectable=ParameterMapService):
        super(AmsafExecutor, self).__init__()
        self._refGroundTruthImage = None
        self._refGroundTruthSeg = None
        self._targetGroundTruthImage = None
        self._targetGroundTruthSeg = None
        self._rigidParameterPriors = None
        self._affineParameterPriors = None
        self._bSplineParameterPriors = None
        self._parameterPriors = {
            'rigid': None,
            'affine': None,
            'bSpline': None
        }
        self._similarityMetric = self.diceScore
        self._segResultsCollection = []
        self._parameterMapService = parameterMapServiceInjectable()

    #######################
    # Getters and Setters #
    #######################

    @property
    def refGroundTruthImage(self):
        return self._refGroundTruthImage

    @refGroundTruthImage.setter
    def refGroundTruthImage(self, value):
        self._refGroundTruthImage = value

    @property
    def refGroundTruthSeg(self):
        return self._refGroundTruthSeg

    @refGroundTruthSeg.setter
    def refGroundTruthSeg(self, value):
        self._refGroundTruthSeg = value

    @property
    def targetGroundTruthImage(self):
        return self._targetGroundTruthImage

    @targetGroundTruthImage.setter
    def targetGroundTruthImage(self, value):
        self._targetGroundTruthImage = value

    @property
    def targetGroundTruthSeg(self):
        return self._targetGroundTruthSeg

    @targetGroundTruthSeg.setter
    def targetGroundTruthSeg(self, value):
        self._targetGroundTruthSeg = value

    @property
    def rigidParameterPriors(self):
        return self._rigidParameterPriors

    @rigidParameterPriors.setter
    def rigidParameterPriors(self, value):
        self._rigidParameterPriors = value
        self._parameterPriors['rigid'] = value

    @property
    def affineParameterPriors(self):
        return self._affineParameterPriors

    @affineParameterPriors.setter
    def affineParameterPriors(self, value):
        self._affineParameterPriors = value
        self._parameterPriors['affine'] = value

    @property
    def bSplineParameterPriors(self):
        return self._bSplineParameterPriors

    @bSplineParameterPriors.setter
    def bSplineParameterPriors(self, value):
        self._bSplineParameterPriors = value
        self._parameterPriors['bSpline'] = value

    @property
    def parameterPriors(self):
        return self._parameterPriors

    @parameterPriors.setter
    def parameterPriors(self, value):
        self._parameterPriors = value

    @property
    def similarityMetric(self):
        return self._similarityMetric

    @similarityMetric.setter
    def similarityMetric(self, value):
        if value == 'subtraction':
            self._similarityMetric = self.subtractionScore
        elif value == 'dice':
            self._similarityMetric = self.diceScore
        elif value == 'jaccard':
            self._similarityMetric = self.jaccardScore
        elif value == 'volumeSimilarity':
            self._similarityMetric = self.volumeSimilarityScore
        elif value == 'kappa':
            self._similarityMetric = self.kappaScore
        else:
            raise ValueError('INVALID SIMILARITY METRIC')

    @property
    def segResultsCollection(self):
        return self._segResultsCollection

    @segResultsCollection.setter
    def segResultsCollection(self, value):
        self._segResultsCollection = value

    @property
    def parameterMapService(self):
        return self._parameterMapService

    @parameterMapService.setter
    def parameterMapService(self, value):
        self._parameterMapService = value

    ###########
    # Methods #
    ###########

    def findTransformParameterMap(self, parameterMapVec):
        # type: ([sitk.ParameterMap]) -> (sitk.ParameterMap, sitk.ParameterMap, sitk.ParameterMap)

        # Initialize Elastix registration
        elastixImageFilter = sitk.ElastixImageFilter()
        elastixImageFilter.LogToConsoleOff()
        elastixImageFilter.SetFixedImage(self.targetGroundTruthImage)
        elastixImageFilter.SetMovingImage(self.refGroundTruthImage)
        elastixImageFilter.SetParameterMap(parameterMapVec[0])
        elastixImageFilter.AddParameterMap(parameterMapVec[1])
        elastixImageFilter.AddParameterMap(parameterMapVec[2])

        # Execute Registration
        elastixImageFilter.Execute()

        return elastixImageFilter.GetTransformParameterMap()

    def findResultSeg(self, transformParameterMapVec, copyMetaData=False):
        # type: ([sitk.ParameterMap], bool) -> sitk.Image

        # Use nearest neighbors interpolator for segmentations
        for tMap in transformParameterMapVec:
            tMap['ResampleInterpolator'] = ['FinalNearestNeighborInterpolator']

        # Initialize Transformix
        transformixImageFilter = sitk.TransformixImageFilter()
        transformixImageFilter.LogToConsoleOff()
        transformixImageFilter.SetMovingImage(self.refGroundTruthSeg)
        transformixImageFilter.SetTransformParameterMap(transformParameterMapVec)

        # Execute transformation
        transformixImageFilter.Execute()

        resultSeg = transformixImageFilter.GetResultImage()

        if copyMetaData:
            resultSeg = self.copyMetaData(self.targetGroundTruthSeg, resultSeg)

        return resultSeg

    @staticmethod
    def copyMetaData(targetImage, movingImage):
        # type: (sitk.Image, sitk.Image) -> sitk.Image

        # Cast voxel types to make images comparable
        processedMovingImage = sitk.Cast(movingImage, targetImage.GetPixelID())

        # Copy header information to make images comparable
        targetImage.CopyInformation(processedMovingImage)
        return processedMovingImage

    def subtractionScore(self, seg):
        # type: (sitk.Image) -> float

        subSeg = self.targetGroundTruthSeg - seg
        statsFilter = sitk.StatisticsImageFilter()
        statsFilter.Execute(subSeg == 0)  # read as: 1 if 0 else 0 for voxel in subSeg

        # sum of ones
        return statsFilter.GetSum()

    def _getOverLapFilter(self, seg):
        # type: (sitk.Image) -> sitk.LabelOverlapMeasuresImageFilter

        overlapFilter = sitk.LabelOverlapMeasuresImageFilter()
        overlapFilter.Execute(self.targetGroundTruthSeg, seg)
        return overlapFilter

    def diceScore(self, seg):
        # type: (sitk.Image) -> float

        overlapFilter = self._getOverLapFilter(seg)
        return overlapFilter.GetDiceCoefficient()

    def jaccardScore(self, seg):
        # type: (sitk.Image) -> float

        overlapFilter = self._getOverLapFilter(seg)
        return overlapFilter.GetJaccardCoefficient()

    def volumeSimilarityScore(self, seg):
        # type: (sitk.Image) -> float

        overlapFilter = self._getOverLapFilter(seg)
        return overlapFilter.GetVolumeSimilarity()

    def kappaScore(self, seg):
        # type: (sitk.Image) -> float

        similarityFilter = sitk.SimilarityIndexImageFilter()
        similarityFilter.Execute(self.targetGroundTruthSeg, seg)
        return similarityFilter.GetSimilarityIndex()

    def execute(self):
        # type: () -> [(sitk.ParameterMap, float)]

        if self.rigidParameterPriors or self.affineParameterPriors or self.bSplineParameterPriors:
            self.parameterMapService.addParameterPriors(self.parameterPriors)

        i = 0
        for pMapVec in self.parameterMapService.generateParameterMaps():
            # Register images to find transformation parameters

            print("\n")
            print("BEGIN ITERATION " + str(i))
            print("\n")

            print("Evaluating parameter map vector: [")
            print("\n")
            for pMapPrinting in pMapVec:
                sitk.PrintParameterMap(pMapPrinting)
                print('\n')
            print("]")
            print("\n")

            print("Finding transform parameter map vector for iteration " + str(i) + "...")
            transformParameterMapVec = self.findTransformParameterMap(pMapVec)

            print("Segmenting moving image for iteration " + str(i) + "...")

            # Transform ref segmentation
            resultSeg = self.findResultSeg(transformParameterMapVec, copyMetaData=True)

            print("Evaluating segmentation accuracy for iteration + " + str(i) + "...")

            # Quantify segmentation accuracy
            segScore = self.similarityMetric(resultSeg)

            # append registration parameters and corresponding score to a list
            self.segResultsCollection.append((pMapVec, segScore))

            print("\n")
            print("============================================")
            print("END ITERATION " + str(i))
            print("SEG SCORE: " + str(segScore))
            print("============================================")
            print("\n")
            print("###################################################################################################")

            i += 1

    def getTopNParameterMapsAndSegScores(self, n):
        return heapq.nlargest(n, self.segResultsCollection, key=lambda x: x[1])  # return the n best results

    def getTopNParameterMaps(self, n):
        return [result[0] for result in self.getTopNParameterMapsAndSegScores(n)]

    def writeTopNParameterMaps(self, n, dirPath):
        if dirPath[-1] != '/':
            dirPath += '/'

        for i, (pMapVec, segScore) in enumerate(self.getTopNParameterMapsAndSegScores(n)):
            for transformMap, transformType in zip(pMapVec, ['Rigid', 'Affine', 'Bspline']):
                writeFileName = dirPath + 'SegResult.' + transformType + '.' + str(i) + '.txt'
                try:
                    sitk.WriteParameterFile(transformMap, writeFileName)
                except Exception:
                    sitk.PrintParameterMap(transformMap)
            f = open(dirPath + 'ParamMapsIterScore.' + str(i) + '.txt', 'a')
            f.write('score: ' + str(segScore) + '\n')
            f.close()

    def getTopNSegmentations(self, n):
        resultSegmentations = []
        for pMapVec in self.getTopNParameterMaps(n):
            transformParameterMapVec = self.findTransformParameterMap(pMapVec)
            resultSegmentations.append(self.findResultSeg(transformParameterMapVec))

        return resultSegmentations
