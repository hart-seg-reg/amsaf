import SimpleITK as sitk
import amsaf
import cropping
import sys

def run_amsaf():
    unsegmented_image = sitk.Cast(amsaf.read_image("../../../../srv/ultrasound_data/30deg/trial10_30_w1_volume_TRANS.nii"),
                                  sitk.sitkUInt16)
    ground_truth = sitk.Cast(amsaf.read_image("../../../../srv/ultrasound_data/30deg/trial10_30_w1_seg2_TRANS.nii"),
                             sitk.sitkUInt16)
    segmented_image = sitk.Cast(amsaf.read_image("../../../../srv/ultrasound_data/30deg/trial12_30_w3_volume_TRANS.nii"),
                                sitk.sitkUInt16)
    segmentation = sitk.Cast(amsaf.read_image("../../../../srv/ultrasound_data/30deg/trial12_30_w3_seg_ak2_TRANS.nii"),
                             sitk.sitkUInt16)

    amsaf_results = amsaf.amsaf_eval(unsegmented_image, ground_truth, segmented_image, segmentation, verbose=True, memoize=False)
    amsaf.write_top_k(10, amsaf_results, '../../../../home/chris/amsaf_results')


def run_split(parameters):






def run_crop(parameters):




if __name__ == '__main__':
    if sys.argv[0] == "split":
      run_split(sys.argv)
    elif sys.argv[0] == "crop":
      run_crop(sys.argv)
    else:
      run_amsaf()
