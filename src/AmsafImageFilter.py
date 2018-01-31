from AmsafExecutor import AmsafExecutor


class AmsafImageFilter(object):
    """Public interface for AMSAF.

    This class provides an interface for AMSAF consistent with SimpleITK style and conventions.
    AmsafExecutor is responsible for implementing most of AmsafImageFilter's behavior.
    See AmsafExecutor for implementation details.

    Public Methods:
        SetRefGroundTruthImage,
        SetRefGroundTruthSeg,
        SetTargetGroundTruthImage,
        SetTargetGroundTruthSeg,
        SetRigidParameterPriors,
        SetAffineParameterPriors,
        SetBSplineParameterPriors,
        SetSimilarityMetric,
        Execute,
        GetTopNParameterMapsAndSegScores,
        GetTopNParameterMaps,
        WriteTopNParameterMaps,
        GetTopNSegmentations
    """
    def __init__(self):
        super(AmsafImageFilter, self).__init__()
        self._amsafExecutor = AmsafExecutor()

    def SetRefGroundTruthImage(self, refGroundTruthImage):
        """Sets reference subject's ground truth image crop.

        Sets the reference subject's image crop corresponding to the target subject's image crop which has been
        segmented and will be treated as a ground truth.

        Args:
            refGroundTruthImage (SimpleITK.Image): Reference subject's corresponding ground truth image crop.
        """
        self._amsafExecutor.refGroundTruthImage = refGroundTruthImage

    def SetRefGroundTruthSeg(self, refGroundTruthSeg):
        """Sets reference subject's ground truth segmentation crop.

        Sets the reference subject's segmentation crop corresponding to the target subject's segmentation crop
        which will be treated as a ground truth.

        Args:
            refGroundTruthSeg (SimpleITK.Image): Reference subject's ground truth segmentation crop.
        """
        self._amsafExecutor.refGroundTruthSeg = refGroundTruthSeg

    def SetTargetGroundTruthImage(self, targetGroundTruthImage):
        """Sets target subject's ground truth image crop.

        Sets the target subject's image crop which corresponds to the target subject's segmented crop, which will
        be treated as a ground truth.

        Args:
            targetGroundTruthImage (SimpleITK.Image): Target subject's ground truth image crop.
        """
        self._amsafExecutor.targetGroundTruthImage = targetGroundTruthImage

    def SetTargetGroundTruthSeg(self, targetGroundTruthImage):
        """Sets the target subjects ground truth segmentation crop.

        Sets the segmentation crop from the target image. This segmentation will be treated as a ground truth.

        Args:
            targetGroundTruthImage (SimpleITK.Image):
        """
        self._amsafExecutor.targetGroundTruthSeg = targetGroundTruthImage

    def SetRigidParameterPriors(self, rigidParameterPriors):
        """Set prior parameter values for rigid component of Elastix registration.

        AMSAF uses a comprehensive grid search to evaluate each combination of selected registration parameters. This
        method allows one to set known or suspected values for parameters in order to reduce the search space.

        Args:
            rigidParameterPriors (dict): A dictionary mapping each parameter to a list of (usually one) possible
                value(s). For example:
                {
                    'MaximumNumberOfIterations': ['512'],
                    'ResampleInterpolator': ['FinalBSplineInterpolator', 'FinalNearestNeighborInterpolator']
                }
        """
        self._amsafExecutor.rigidParameterPriors = rigidParameterPriors

    def SetAffineParameterPriors(self, affineParameterPriors):
        """Set prior parameter values for rigid component of Elastix registration.

        AMSAF uses a comprehensive grid search to evaluate each combination of selected registration parameters. This
        method allows one to set known or suspected values for parameters in order to reduce the search space.

        Args:
            affineParameterPriors (dict): A dictionary mapping each parameter to a list of (usually one) possible
                value(s). For example:
                {
                    'MaximumNumberOfIterations': ['512'],
                    'ResampleInterpolator': ['FinalBSplineInterpolator', 'FinalNearestNeighborInterpolator']
                }
        """
        self._amsafExecutor.affineParameterPriors = affineParameterPriors

    def SetBSplineParameterPriors(self, bSplineParameterPriors):
        """Set prior parameter values for rigid component of Elastix registration.

        AMSAF uses a comprehensive grid search to evaluate each combination of selected registration parameters. This
        method allows one to set known or suspected values for parameters in order to reduce the search space.

        Args:
            bSplineParameterPriors (dict): A dictionary mapping each parameter to a list of (usually one) possible
                value(s). For example:
                {
                    'MaximumNumberOfIterations': ['512'],
                    'ResampleInterpolator': ['FinalBSplineInterpolator', 'FinalNearestNeighborInterpolator']
                }
        """
        self._amsafExecutor.bSplineParameterPriors = bSplineParameterPriors

    def SetSimilarityMetric(self, similarityMetric):
        """Sets similarity metric used to evaluate segmentations during grid search.

        The default similarity metric is the Dice coefficient:
            https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient

        Args:
            similarityMetric (str): A string corresponding to an available AMSAF similarity metric.
                Possible options are: 'subtraction', 'dice', 'jaccard', 'volumeSimilarity', 'kappa'
        """
        self._amsafExecutor.similarityMetric = similarityMetric

    def Execute(self):
        """Executes AMSAF parameter optimization. Depending on the size of the parameter space, this may
        take more than a few hours, and should be run on a server if time is any constraint. This method must be
        called before any results can be extracted through methods listed below.
        """
        self._amsafExecutor.execute()

    def GetTopNParameterMapsAndSegScores(self, n):
        """Gets a list of tuples of top n parameter maps and corresponding scores.

        The returned list will be an ordered series of ordered pairs. Each pair consists of, firstly, a SimpleITK
        parameter map used for Elastix registration, and secondly, its corresponding score. The list is ordered from
        best result to worst result.

        Args:
            n (int): The number of results to return.

        Returns:
            List or ordered pairs (sitk.ParameterMap, float) ordered from best to worst score.
        """
        return self._amsafExecutor.getTopNParameterMapsAndSegScores(n)

    def GetTopNParameterMaps(self, n):
        return self._amsafExecutor.getTopNParameterMaps(n)

    def WriteTopNParameterMaps(self, n, dirPath):
        self._amsafExecutor.writeTopNParameterMaps(n, dirPath)

    def GetTopNSegmentations(self, n):
        return self._amsafExecutor.getTopNSegmentations(n)
