import unittest
import SimpleITK as sitk
from amsaf.AmsafExecutor import AmsafExecutor
import MockClasses

PQ_forearm_img_cropped = sitk.ReadImage(
    "/srv/hart_mri/mri_data/PQ_Full/crops/forearm/PQ_forearm_cropped_for_ITK-SNAP_biascorr.nii")

PQ_forearm_muscles = sitk.ReadImage("/srv/hart_mri/mri_data/PQ_Full/crops/forearm/PQ_forearm_cropped_muscles.nii")

sub3_forearm_img_cropped = sitk.ReadImage(
    "/srv/hart_mri/mri_data/SUBJECT_3/2-forearm/crops/sub3_forearm_cropped_for_ITK-SNAP.nii")

sub3_forearm_muscles_ground_truth = sitk.ReadImage(
    "/srv/hart_mri/mri_data/SUBJECT_3/2-forearm/crops/sub3_forearm_cropped_ground_truth_muscles.nii")


class TestAmsafExecutor(unittest.TestCase):
    def setUp(self):
        self.rigidParameterMap = sitk.GetDefaultParameterMap('rigid')
        self.rigidParameterMap['AutomaticParameterEstimation'] = ['true']
        self.rigidParameterMap['AutomaticTransformInitialization'] = ['true']
        self.affineParameterMap = sitk.GetDefaultParameterMap('affine')
        self.bSplineParameterMap = sitk.GetDefaultParameterMap('bspline')

        self.amsafExecutor = AmsafExecutor()
        self.amsafExecutor.targetGroundTruthImage = sub3_forearm_img_cropped
        self.amsafExecutor.targetGroundTruthSeg = sub3_forearm_muscles_ground_truth
        self.amsafExecutor.refGroundTruthImage = PQ_forearm_img_cropped
        self.amsafExecutor.refGroundTruthSeg = PQ_forearm_muscles

        self.elastixImageFilter = sitk.ElastixImageFilter()
        self.elastixImageFilter.SetFixedImage(sub3_forearm_img_cropped)
        self.elastixImageFilter.SetMovingImage(PQ_forearm_img_cropped)
        self.elastixImageFilter.SetParameterMap(self.rigidParameterMap)
        self.elastixImageFilter.AddParameterMap(self.affineParameterMap)
        self.elastixImageFilter.AddParameterMap(self.bSplineParameterMap)

    def tearDown(self):
        self.amsafExecutor = None
        self.elastixImageFilter = None

    def testFindTransformParameterMap(self):
        amsafResult = self.amsafExecutor.findTransformParameterMap(
            [self.rigidParameterMap, self.affineParameterMap, self.bSplineParameterMap])
        self.elastixImageFilter.Execute()

        self.elastixImageFilter.Execute()
        elastixResult = self.elastixImageFilter.GetTransformParameterMap()

        self.assertEqual([result.asdict() for result in amsafResult], [result.asdict() for result in elastixResult])

    def testFindResultSeg(self):
        amsafTransformParameterMapVec = self.amsafExecutor.findTransformParameterMap(
            [self.rigidParameterMap, self.affineParameterMap, self.bSplineParameterMap])

        self.elastixImageFilter.Execute()
        elastixTransformParameterMapVec = self.elastixImageFilter.GetTransformParameterMap()

        transformixImageFilter = sitk.TransformixImageFilter()
        transformixImageFilter.SetMovingImage(PQ_forearm_muscles)
        transformixImageFilter.SetTransformParameterMap(elastixTransformParameterMapVec)

        transformixImageFilter.Execute()

        amsafResult = self.amsafExecutor.findResultSeg(amsafTransformParameterMapVec)
        transformixResult = sitk.Cast(transformixImageFilter.GetResultImage(), amsafResult.GetPixelID())

        amsafResult.CopyInformation(transformixResult)

        similarityFilter = sitk.SimilarityIndexImageFilter()
        similarityFilter.Execute(amsafResult, transformixResult)
        similarityScore = similarityFilter.GetSimilarityIndex()

        self.assertTrue(1.0 - similarityScore < 0.1)

    def testSubtractionScore(self):
        self.amsafExecutor.similarityMetric = 'subtraction'
        simScore = self.amsafExecutor.similarityMetric(sub3_forearm_muscles_ground_truth)

        self.assertEqual(simScore, sub3_forearm_muscles_ground_truth.GetNumberOfPixels())

    def testDiceScore(self):
        self.amsafExecutor.similarityMetric = 'dice'
        simScore = self.amsafExecutor.similarityMetric(sub3_forearm_muscles_ground_truth)

        self.assertEqual(simScore, 1.0)

    def testJaccardScore(self):
        self.amsafExecutor.similarityMetric = 'jaccard'
        simScore = self.amsafExecutor.similarityMetric(sub3_forearm_muscles_ground_truth)
        self.assertEqual(simScore, 1.0)

    def testExecute(self):
        mockParameterMapService = MockClasses.MockParameterMapService

        self.amsafExecutor = AmsafExecutor(mockParameterMapService)
        self.amsafExecutor.targetGroundTruthImage = sub3_forearm_img_cropped
        self.amsafExecutor.targetGroundTruthSeg = sub3_forearm_muscles_ground_truth
        self.amsafExecutor.refGroundTruthImage = PQ_forearm_img_cropped
        self.amsafExecutor.refGroundTruthSeg = PQ_forearm_muscles
        self.amsafExecutor.similarityMetric = 'volumeSimilarity'

        self.amsafExecutor.execute()

        topTwentyMaps = self.amsafExecutor.getTopNParameterMaps(20)
        topTwentyMapsAndScores = self.amsafExecutor.getTopNParameterMapsAndSegScores(20)
        topTwentySegs = self.amsafExecutor.getTopNSegmentations(20)

        self.assertTrue(len(topTwentyMaps) == len(topTwentyMapsAndScores) == len(topTwentySegs) == 1)

    def testGetTopNResults(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
