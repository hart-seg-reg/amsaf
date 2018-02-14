=====
Usage
=====

To use amsaf in a project::

    import amsaf

    # image you want to segment
    unsegmented_image = ...

    # small segmentation slice from unsegmented image which we need in order to
    # score each amsaf result
    ground_truth = ...     

    # image which we want to map a segmentation from
    segmented_image = ...

    # segmentation corresponding to segmented_image
    segmentation = ...

    # create a generator for amsaf result computations
    amsaf_results = amsaf_eval(unsegmentd_image, ground_truth, segmented_image, segmented)

    # evaluate lazy computations, score them, and write them
    write_top_k(10, amsaf_results, '~/amsaf_results')

