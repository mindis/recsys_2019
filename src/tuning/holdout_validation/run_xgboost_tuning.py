import os

import numpy as np

from src.model.Ensemble.Boosting.Boosting import BoostingFixedData
from src.model.Ensemble.Boosting.LightGBMRecommender import LightGBMRecommender


def sample_parameters(parameters: dict):
    keys = list(parameters.keys())
    sample = {}
    for k in keys:
        values = parameters[k]
        n_param = len(values)
        if n_param == 1:
            sample[k] = values[0]
        else:
            idx = np.random.randint(low=0, high=n_param)
            sample[k] = values[idx]

    return sample


def run_xgb_tuning(train_df, valid_df, y_train, non_zero_count, total,
                   URM_train,
                   evaluator,
                   n_trials=40,
                   max_iter_per_trial=30000, n_early_stopping=500,
                   objective="binary:logistic", parameters=None,
                   cutoff=20,
                   best_model_folder="",
                   URM_test=None):
    """
    Run tuning for XGBoost algorithm

    :param train_df: dataframe used for training
    :param valid_df: dataframe used for validation
    :param y_train: training label for train_df
    :param non_zero_count: number of non-zero ratings in train_df
    :param total: total number of interactions in train_df
    :param URM_train: URM_train used for generating y_train
    :param evaluator: evaluator that will be used to validate the algorithm performance
    :param n_trials: number of trials of the tuning algorithm
    :param max_iter_per_trial: max number of epochs for a trial
    :param n_early_stopping: how often the training will do early stopping
    :param objective: function that will be optimized by the algorithm
    :param parameters: custom parameters from which to sample the hyperparameters
    :param cutoff: cutoff at which the boosting dataframe has been created
    :param best_model_folder: where to store the best models
    :return: None
    """
    try:
        if not os.path.exists(best_model_folder):
            os.mkdir(best_model_folder)
    except FileNotFoundError as e:
        os.makedirs(best_model_folder)

    output_folder_file = best_model_folder + "tuning_results.txt"

    scale_pos_weight = (total - non_zero_count) / non_zero_count

    if parameters is None:
        parameters = {"learning_rate": [0.1, 0.01, 0.001, 0.0001],
                      "gamma": [0.001, 0.01, 0.1, 0.3, 0.5, 0.8],  # min loss required to split a leaf
                      "lambda": [0.001, 0.01, 0.1, 1, 10, 100],  # regularizer L2
                      "alpha": [0.001, 0.01, 0.1, 1, 10, 100],  # regularizer L1
                      "max_depth": [2, 4, 7, 11, 15],  # the larger, the higher prob. to overfitting
                      "max_delta_step": [0, 1, 5, 10],  # needed for unbalanced dataset
                      "subsample": [0.2, 0.4, 0.5, 0.6, 0.7],  # sub-sampling of data before growing trees
                      "colsample_bytree": [0.3, 0.6, 0.8, 1.0],  # sub-sampling of columns
                      "scale_pos_weight": [scale_pos_weight],  # to deal with unbalanced dataset
                      "objective": [objective],  # Objective function to be optimized
                      # "eval_metric": ["auc"]
                      }

    f = open(output_folder_file, "w")
    f.write("Tuning XGBoost \n")
    f.write("Parameters: \n " + str(parameters))
    f.write("\n N_trials: {} \n".format(n_trials))
    f.write("Max iteration per trial: {}\n".format(max_iter_per_trial))
    f.write("Early stopping every {} iterations\n".format(n_early_stopping))

    f.write("\n\n Begin tuning \n\n")
    f.flush()

    max_map = -1
    best_param = {}
    best_trial = -1

    for i in range(n_trials):
        sample = sample_parameters(parameters)
        print("Trial {} over {}".format(i, n_trials))
        print("Trying configuration: " + str(sample) + "\n")
        f.write(str(sample))

        boosting = BoostingFixedData(URM_train=URM_train, X=train_df, y=y_train, df_test=valid_df,
                                  cutoff=cutoff, URM_test=URM_test)

        boosting.train(num_round=max_iter_per_trial, param=sample, early_stopping_round=n_early_stopping)

        map_10 = evaluator.evaluateRecommender(boosting)[0][10]['MAP']
        if map_10 > max_map:
            print("New best config found\n")
            max_map = map_10
            best_param = sample
            best_trial = i
            print("Saving best model...", end="")
            boosting.save_model(best_model_folder, "best_model_{}.bin".format(i))
            print("Done")

        print("Curr val: {}\n".format(map_10))
        f.write("Map@10 {}\n".format(map_10))
        f.flush()

    # Best results
    f.write("\n\n")
    f.write("Best MAP score: {}\n".format(max_map))
    f.write("Best config " + str(best_param) + "\n")
    f.write("Best trial " + str(best_trial) + "\n")
    f.close()


def run_lgb_tuning(train_df, valid_df, y_train, non_zero_count, total,
                   URM_train,
                   evaluator,
                   n_trials=40,
                   max_iter_per_trial=10000, n_early_stopping=100,
                   objective="lambdarank", parameters=None,
                   cutoff=20,
                   best_model_folder="",
                   URM_test=None):
    """
    Run tuning for LightGBM algorithm

    :param train_df: dataframe used for training
    :param valid_df: dataframe used for validation
    :param y_train: training label for train_df
    :param non_zero_count: number of non-zero ratings in train_df
    :param total: total number of interactions in train_df
    :param URM_train: URM_train used for generating y_train
    :param evaluator: evaluator that will be used to validate the algorithm performance
    :param n_trials: number of trials of the tuning algorithm
    :param max_iter_per_trial: max number of epochs for a trial
    :param n_early_stopping: how often the training will do early stopping
    :param objective: function that will be optimized by the algorithm
    :param parameters: custom parameters from which to sample the hyperparameters
    :param cutoff: cutoff at which the boosting dataframe has been created
    :param best_model_folder: where to store the best models
    :return: None
    """
    try:
        if not os.path.exists(best_model_folder):
            os.mkdir(best_model_folder)
    except FileNotFoundError as e:
        os.makedirs(best_model_folder)

    output_folder_file = best_model_folder + "tuning_results.txt"

    if parameters is None:
        parameters = {"learning_rate": [10 ** -i for i in range(2, 8)],  # Fixed learning rate and then decrease it if necessary on the future
                      "min_gain_to_split": [0.001, 0.01, 0.1, 0.3, 0.5, 0.8],  # min loss required to split a leaf
                      "lambda_l1": [0.001, 0.01, 0.1, 1, 10, 100],  # regularizer L1
                      "lambda_l2": [0.001, 0.01, 0.1, 1, 10, 100],  # regularizer L2
                      "max_depth": [2, 4, 7, 11, 15, 32, 64],  # the larger, the higher prob. to overfitting
                      "min_data_in_leaf": [5, 10, 20, 30, 60],
                      "bagging_fraction": [0.1*step for step in range(1, 10)],
                      "bagging_freq": [2, 4, 8, 16, 32],
                      "feature_fraction": [0.1*step for step in range(1, 10)],
                      "num_leaves": [32, 48, 64, 128, 256],  # max number of leaves in a tree
                      "objective": [objective],  # Objective function to be optimized
                      "metric": ["map"],
                      "eval_at": [[10]],
                      "max_position": [10],
                      "is_provide_training_metric": [True]
                      }

    f = open(output_folder_file, "w")
    f.write("Tuning LightGBM \n")
    f.write("Parameters: \n " + str(parameters))
    f.write("\n N_trials: {} \n".format(n_trials))
    f.write("Max iteration per trial: {}\n".format(max_iter_per_trial))
    f.write("Early stopping every {} iterations\n".format(n_early_stopping))

    f.write("\n\n Begin tuning \n\n")
    f.flush()

    max_map = -1
    best_param = {}
    best_trial = -1

    for i in range(n_trials):
        sample = sample_parameters(parameters)
        print("Trial {} over {}".format(i, n_trials))
        print("Trying configuration: " + str(sample) + "\n")
        f.write(str(sample))

        boosting = LightGBMRecommender(URM_train=URM_train, X_train=train_df, y_train=y_train, X_test=valid_df,
                                       cutoff_test=cutoff, URM_test=URM_test)

        boosting.train(num_round=max_iter_per_trial, param=sample, early_stopping_round=n_early_stopping)

        map_10 = evaluator.evaluateRecommender(boosting)[0][10]['MAP']
        if map_10 > max_map:
            print("New best config found\n")
            max_map = map_10
            best_param = sample
            best_trial = i
            print("Saving best model...", end="")
            boosting.save_model(best_model_folder, "best_model_{}.bin".format(i))
            print("Done")

        print("Curr val: {}\n".format(map_10))
        f.write("Map@10 {}\n".format(map_10))
        f.flush()

    # Best results
    f.write("\n\n")
    f.write("Best MAP score: {}\n".format(max_map))
    f.write("Best config " + str(best_param) + "\n")
    f.write("Best trial " + str(best_trial) + "\n")
    f.close()
