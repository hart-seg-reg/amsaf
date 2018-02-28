import amsaf.amsaf as af
import SimpleITK as sitk

"""
Go to GDrive /Ultrasound sandbox/Sub1/aligned_scans/30deg
Pick some image(one reference image with its segmentation, and one unsegmented image).
Run the following code and we can get the segmentation using default parameter.
"""


def testDefaultPara():
    unsegmented_image = af.read_image("/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/trial10_30_w1_volume.nii")
    segmented_image = af.read_image("/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/trial12_30_w3_volume.nii")
    segmentation = af.read_image("/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/trial12_30_w3_seg_ak2.nii")

    segment_result = af.segment(unsegmented_image, segmented_image, segmentation)

    sitk.WriteImage(segment_result, "/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/test_result(trial10).nii")


def test_amsaf_eval():
    para = list()
    unsegmented_image = af.read_image("~../srv/ultrasound_data/30deg/trial10_30_w1_volume_TRANS.nii")
    segmented_image = af.read_image("~../srv/ultrasound_data/30deg/trial12_30_w3_volume.nii")
    segmentation = af.read_image("~../srv/ultrasound_data/30deg/trial12_30_w3_seg_ak2.nii")
    print("*********************************")
    for i in af.amsaf_eval(unsegmented_image,
                           ground_truth,
                           segmented_image,
                           segmentation):
        print(i)
        para.append(i)

    print(para)
    file = open('parameter.txt', 'w')
    file.write(str(para))
    file.close()

def test_amsaf():
    unsegmented_image = af.read_image("/srv/ultrasound_data/30deg/trial10_30_w1_volume_TRANS.nii")
    ground_truth = af.read_image("/srv/ultrasound_data/30deg/trial10_30_w1_seg2_TRANS.nii")
    segmented_image = af.read_image("/srv/ultrasound_data/30deg/trial12_30_w3_volume_TRANS.nii")
    segmentation = af.read_image("/srv/ultrasound_data/30deg/trial12_30_w3_seg_ak2_TRANS.nii")
    amsaf_results = af.amsaf_eval(unsegmented_image, ground_truth,segmented_image,segmentation)
    af.write_top_k(100,amsaf_results, '~/amsaf_results')
def main():
    # testDefaultPara()
    test_amsaf()


if __name__ == '__main__': main()
