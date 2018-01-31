import SimpleITK as sitk
import itertools

import pytest
from amsaf import amsaf_func as af

fixed_image = af.read_image(
    "/srv/hart_mri/mri_data/SUBJECT_3/2-forearm/crops/sub3_forearm_cropped_for_ITK-SNAP_biascorr.nii"
)
moving_image = af.read_image(
    "/srv/hart_mri/mri_data/PQ_Full/crops/forearm/PQ_forearm_cropped_for_ITK-SNAP_biascorr.nii"
)
PQ_forearm_combined = af.read_image(
    "/srv/hart_mri/mri_data/PQ_Full/crops/forearm/PQ_forearm_cropped_combined.nii"
)

sub3_forearm_combined_gt = af.read_image(
    "/srv/hart_mri/mri_data/SUBJECT_3/2-forearm/crops/sub3_forearm_cropped_combined.nii"
)


def test_amsaf_rank():
    results = list(
        itertools.islice(
            af.amsaf_rank(
                fixed_image,
                moving_image,
                sub3_forearm_combined_gt,
                PQ_forearm_combined,
                verbose=True), 0, 2))

    af.write_top_k(2, results, 'temp-test-results')


def test_segment():
    return
    af.segment(fixed_image, moving_image, PQ_forearm_combined)


def test_register():
    return
    _, parameter_maps = af.register(fixed_image, moving_image, verbose=True)
    for i, pm in enumerate(parameter_maps):
        sitk.WriteParameterFile(pm, "./test_transform_%s" % i)


def test_transform():
    return

    def get_transform_pmaps():
        result = []
        for i in range(3):
            result.append(
                sitk.ReadParameterFile(
                    './test_data/TransformParameters.%s.txt' % i))
        return result

    af.transform(PQ_forearm_combined, get_transform_pmaps())


if __name__ == '__main__':
    pytest.main()
