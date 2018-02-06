import amsaf as af
import SimpleITK as sitk

unsegmented_image = af.read_image("/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/trial10_30_w1_volume.nii")
segmented_image = af.read_image("/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/trial12_30_w3_volume.nii")
segmentation = af.read_image("/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/trial12_30_w3_seg_ak2.nii")

segment_result = af.segment(unsegmented_image, segmented_image, segmentation)

sitk.WriteImage(segment_result, "/mnt/c/Users/shuyi/OneDrive/HARU/Test Data/test_result.nii")
