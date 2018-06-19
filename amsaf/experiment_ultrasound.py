import SimpleITK as sitk
import amsaf
import sys

def run_amsaf():
    directory = "/srv/ultrasound_data/30deg/"
    unsegmented_image = sitk.Cast(amsaf.read_image(directory + "trial10_30_w1_volume_TRANS.nii"),
                                  sitk.sitkUInt16)
    ground_truth = sitk.Cast(amsaf.read_image(directory + "trial10_30_w1_seg2_TRANS.nii"),
                             sitk.sitkUInt16)
    segmented_image = sitk.Cast(amsaf.read_image(directory + "trial12_30_w3_volume_TRANS.nii"),
                                sitk.sitkUInt16)
    segmentation = sitk.Cast(amsaf.read_image(directory + "trial12_30_w3_seg_ak2_TRANS.nii"),
                             sitk.sitkUInt16)

    amsaf_results = amsaf.amsaf_eval(unsegmented_image, ground_truth, segmented_image, segmentation, verbose=True, memoize=False)
    amsaf.write_top_k(10, amsaf_results, '../../../../home/chris/amsaf_results')



if __name__ == '__main__':
  run_amsaf()
