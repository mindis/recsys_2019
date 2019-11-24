from course_lib.Data_manager.DataReader import DataReader
from course_lib.Data_manager.DataReader_utils import merge_ICM
from course_lib.Data_manager.IncrementalSparseMatrix import IncrementalSparseMatrix_FilterIDs
import pandas as pd
import numpy as np


def load_URM(file_path, separator=",", if_new_user="add", if_new_item="add", item_original_ID_to_index=None,
             user_original_ID_to_index=None):
    URM_all_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_col_mapper=item_original_ID_to_index,
                                                        on_new_col=if_new_item,
                                                        preinitialized_row_mapper=user_original_ID_to_index,
                                                        on_new_row=if_new_user)

    df_original = pd.read_csv(filepath_or_buffer=file_path, sep=separator,
                              usecols=['row', 'col'],
                              dtype={'row': str, 'col': str})

    user_id_list = df_original['row'].values
    item_id_list = df_original['col'].values
    rating_list = np.ones(len(user_id_list), dtype=np.float64)

    URM_all_builder.add_data_lists(user_id_list, item_id_list, rating_list)
    return URM_all_builder.get_SparseMatrix(), \
           URM_all_builder.get_column_token_to_id_mapper(), \
           URM_all_builder.get_row_token_to_id_mapper()


def load_ICM_asset(file_path, separator=",", if_new_item="add", item_original_ID_to_index=None):
    ICM_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_row_mapper=item_original_ID_to_index,
                                                    on_new_row=if_new_item)

    df_original = pd.read_csv(file_path, sep=separator,
                              usecols=['row', 'col', 'data'],
                              dtype={'row': str, 'col': str, 'data': float})

    item_id_list = df_original['row'].values
    feature_list = ["asset"] * len(item_id_list)
    data_list = df_original['data'].values

    ICM_builder.add_data_lists(item_id_list, feature_list, data_list)

    return ICM_builder.get_SparseMatrix(), \
           ICM_builder.get_column_token_to_id_mapper(), \
           ICM_builder.get_row_token_to_id_mapper()


def load_ICM_sub_class(file_path, separator=",", if_new_item="add", item_original_ID_to_index=None):
    ICM_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_row_mapper=item_original_ID_to_index,
                                                    on_new_row=if_new_item)

    df_original = pd.read_csv(file_path, sep=separator,
                              usecols=['row', 'col'],
                              dtype={'row': str, 'col': str})

    df_original['col'] = "sub_class-" + df_original['col']

    item_id_list = df_original['row'].values
    sub_class_id_list = df_original['col'].values

    ICM_builder.add_data_lists(item_id_list, sub_class_id_list, np.ones(len(item_id_list), dtype=np.float64))

    return ICM_builder.get_SparseMatrix(), \
           ICM_builder.get_column_token_to_id_mapper(), \
           ICM_builder.get_row_token_to_id_mapper()


def load_ICM_price(file_path, separator=',', if_new_item="add", item_original_ID_to_index=None):
    ICM_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_row_mapper=item_original_ID_to_index,
                                                    on_new_row=if_new_item)

    df_original = pd.read_csv(file_path, sep=separator,
                              usecols=['row', 'col', 'data'],
                              dtype={'row': str, 'col': str, 'data': float})

    item_id_list = df_original['row'].values
    feature_list = ["price"] * len(item_id_list)
    data_list = df_original['data'].values

    ICM_builder.add_data_lists(item_id_list, feature_list, data_list)

    return ICM_builder.get_SparseMatrix(), \
           ICM_builder.get_column_token_to_id_mapper(), \
           ICM_builder.get_row_token_to_id_mapper()


def load_ICM_item_pop(file_path, separator=',', if_new_item="add", item_original_ID_to_index=None):
    ICM_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_row_mapper=item_original_ID_to_index,
                                                    on_new_row=if_new_item)

    df_original = pd.read_csv(file_path, sep=separator,
                              usecols=['row', 'col', 'data'],
                              dtype={'row': str, 'col': str, 'data': float})
    item_pop = df_original.groupby(by='col')['data'].sum()
    item_pop = (item_pop - 0)/(item_pop.max() - 0)

    item_id_list = item_pop.index
    feature_list = ["item_pop"] * len(item_id_list)
    data_list = item_pop.values.astype(np.float64)

    ICM_builder.add_data_lists(item_id_list, feature_list, data_list)

    return ICM_builder.get_SparseMatrix(), \
           ICM_builder.get_column_token_to_id_mapper(), \
           ICM_builder.get_row_token_to_id_mapper()


def load_UCM_age(file_path, separator=",", if_new_user="add", user_original_ID_to_index=None):
    UCM_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_row_mapper=user_original_ID_to_index,
                                                    on_new_row=if_new_user)

    df_original = pd.read_csv(file_path, sep=separator, usecols=['row', 'col'], dtype={'row': str, 'col': str})

    user_id_list = df_original['row'].values
    age_id_list = df_original['col'].values

    UCM_builder.add_data_lists(user_id_list, age_id_list, np.ones(len(user_id_list), dtype=np.float64))

    return UCM_builder.get_SparseMatrix(), UCM_builder.get_column_token_to_id_mapper(), \
           UCM_builder.get_row_token_to_id_mapper()


def load_UCM_region(file_path, separator=",", if_new_user="add", user_original_ID_to_index=None):
    UCM_builder = IncrementalSparseMatrix_FilterIDs(preinitialized_row_mapper=user_original_ID_to_index,
                                                    on_new_row=if_new_user)

    df_original = pd.read_csv(file_path, sep=separator, usecols=['row', 'col'], dtype={'row': str, 'col': str})

    user_id_list = df_original['row'].values
    region_id_list = df_original['col'].values

    UCM_builder.add_data_lists(user_id_list, region_id_list, np.ones(len(user_id_list), dtype=np.float64))

    return UCM_builder.get_SparseMatrix(), UCM_builder.get_column_token_to_id_mapper(), \
           UCM_builder.get_row_token_to_id_mapper()

def build_ICM_all(ICM_object_dict, ICM_feature_mapper_dict):
    ICM_all = None
    tokenToFeatureMapper_ICM_all = {}
    for ICM_name, ICM_object in ICM_object_dict.items():
        if ICM_name != "ICM_all":
            if ICM_all is None:
                ICM_all = ICM_object.copy()
                tokenToFeatureMapper_ICM_all = ICM_feature_mapper_dict[ICM_name]
            else:
                ICM_all, tokenToFeatureMapper_ICM_all = merge_ICM(ICM_all, ICM_object,
                                                                  tokenToFeatureMapper_ICM_all,
                                                                  ICM_feature_mapper_dict[ICM_name])

    return ICM_all, tokenToFeatureMapper_ICM_all

def get_ICM_numerical(reader: DataReader, with_item_popularity = True):
    ICM_asset = reader.get_ICM_from_name("ICM_asset")
    ICM_price = reader.get_ICM_from_name("ICM_price")
    ICM_asset_mapper = reader.get_ICM_feature_to_index_mapper_from_name("ICM_asset")
    ICM_price_mapper = reader.get_ICM_feature_to_index_mapper_from_name("ICM_price")

    ICM_numerical, ICM_numerical_mapper = merge_ICM(ICM_asset, ICM_price, ICM_asset_mapper, ICM_price_mapper)
    if with_item_popularity:
        ICM_item_pop = reader.get_ICM_from_name("ICM_item_pop")
        ICM_item_pop_mapper = reader.get_ICM_feature_to_index_mapper_from_name("ICM_item_pop")
        ICM_numerical, ICM_numerical_mapper = merge_ICM(ICM_numerical, ICM_item_pop, ICM_numerical_mapper,
                                                        ICM_item_pop_mapper)
    return ICM_numerical, ICM_numerical_mapper