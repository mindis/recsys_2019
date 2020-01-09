import os
from datetime import datetime
import numpy as np

from skopt.space import Categorical, Integer

from course_lib.Base.BaseRecommender import BaseRecommender
from course_lib.Base.Evaluation.Evaluator import EvaluatorHoldout
from scripts.model_selection.cross_validate_utils import get_seed_list, write_results_on_file
from scripts.scripts_utils import read_split_load_data
from src.data_management.data_reader import get_UCM_train, get_ICM_train_new, get_ignore_users, get_UCM_train_new
from src.model import best_models_lower_threshold_23, best_models_upper_threshold_22, k_1_out_best_models
from src.model import new_best_models
from src.model.Ensemble.BaggingMergeRecommender import BaggingMergeItemSimilarityRecommender
from src.model.HybridRecommender.HybridDemographicRecommender import HybridDemographicRecommender
from src.model.KNN.ItemKNNDotCFRecommender import ItemKNNDotCFRecommender
from src.tuning.cross_validation.CrossSearchAbstractClass import compute_mean_std_result_dict, get_result_string
from src.utils.general_utility_functions import get_project_root_path

# CONSTANTS TO MODIFY
K_OUT = 1
CUTOFF = 10
ALLOW_COLD_USERS = False
LOWER_THRESHOLD = -1  # Remove users below or equal this threshold (default value: -1)
UPPER_THRESHOLD = 2 ** 16 - 1  # Remove users above or equal this threshold (default value: 2**16-1)
IGNORE_NON_TARGET_USERS = True

AGE_TO_KEEP = []  # Default []

# VARIABLES TO MODIFY
model_name = "HybridDemographic_T_23"


def get_model(URM_train, ICM_train, UCM_train):
    threshold = 23
    lt_23_recommender = best_models_lower_threshold_23.WeightedAverageItemBasedWithRP3.get_model(URM_train,
                                                                                                 ICM_train)
    ut_22_recommender = best_models_upper_threshold_22.WeightedAverageAll.get_model(URM_train, ICM_train, UCM_train)
    lt_23_users_mask = np.ediff1d(URM_train.tocsr().indptr) >= threshold
    lt_23_users = np.arange(URM_train.shape[0])[lt_23_users_mask]
    ut_23_users = np.arange(URM_train.shape[0])[~lt_23_users_mask]

    main_recommender = HybridDemographicRecommender(URM_train=URM_train)
    main_recommender.add_user_group(1, lt_23_users)
    main_recommender.add_user_group(2, ut_23_users)
    main_recommender.add_relation_recommender_group(lt_23_recommender, 1)
    main_recommender.add_relation_recommender_group(ut_22_recommender, 2)
    main_recommender.fit()
    return main_recommender


def main():
    seed_list = get_seed_list()

    results_list = []
    for i in range(0, len(seed_list)):
        data_reader = read_split_load_data(K_OUT, ALLOW_COLD_USERS, seed_list[i])

        URM_train, URM_test = data_reader.get_holdout_split()
        ICM_all, _ = get_ICM_train_new(data_reader)
        UCM_all, _ = get_UCM_train_new(data_reader)

        # Setting evaluator
        ignore_users = get_ignore_users(URM_train, data_reader.get_original_user_id_to_index_mapper(),
                                        lower_threshold=LOWER_THRESHOLD, upper_threshold=UPPER_THRESHOLD,
                                        ignore_non_target_users=IGNORE_NON_TARGET_USERS)

        single_evaluator = EvaluatorHoldout(URM_test, cutoff_list=[CUTOFF], ignore_users=ignore_users)

        # Get model
        model: BaseRecommender = get_model(URM_train, ICM_all, UCM_all)

        result_dict = single_evaluator.evaluateRecommender(model)[0][CUTOFF]
        print("FOLD-{} RESULT: {} \n".format(i + 1, result_dict))
        results_list.append(result_dict)

    mean_result_dict, std_result_dict = compute_mean_std_result_dict(results_list)
    results = get_result_string(mean_result_dict, std_result_dict)

    # Store results on file
    date_string = datetime.now().strftime('%b%d_%H-%M-%S')
    cross_valid_path = os.path.join(get_project_root_path(), "report/cross_validation/")
    file_path = os.path.join(cross_valid_path, "cross_valid_model_{}.txt".format(date_string))
    write_results_on_file(file_path, model_name, {}, len(seed_list), seed_list, results)


if __name__ == '__main__':
    main()
