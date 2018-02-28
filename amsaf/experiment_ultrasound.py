import SimpleITK as sitk
import amsaf


def run_amsaf():
    unsegmented_image = sitk.Cast(amsaf.read_image("/srv/ultrasound_data/30deg/trial10_30_w1_volume_TRANS.nii"),
                                  sitk.sitkFloat32)
    ground_truth = sitk.Cast(amsaf.read_image("/srv/ultrasound_data/30deg/trial10_30_w1_seg2_TRANS.nii"),
                             sitk.sitkFloat32)
    segmented_image = sitk.Cast(amsaf.read_image("/srv/ultrasound_data/30deg/trial12_30_w3_volume_TRANS.nii"),
                                sitk.sitkFloat32)
    segmentation = sitk.Cast(amsaf.read_image("/srv/ultrasound_data/30deg/trial12_30_w3_seg_ak2_TRANS.nii"),
                             sitk.sitkFloat32)

    amsaf_results = amsaf.amsaf_eval(unsegmented_image, ground_truth, segmented_image, segmentation, verbose=True)
    amsaf.write_top_k(10, amsaf_results, '/home/ian/amsaf_results')


if __name__ == '__main__':
    run_amsaf()
