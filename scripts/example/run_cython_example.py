from course_lib.KNN.UserKNNCFRecommender import UserKNNCFRecommender
from src.data_management.RecSys2019Reader import RecSys2019Reader
from course_lib.Data_manager.DataSplitter_k_fold import DataSplitter_Warm_k_fold

if __name__ == '__main__':
    dataset = RecSys2019Reader("../../data/")
    dataset = DataSplitter_Warm_k_fold(dataset, n_folds=10)
    dataset.load_data()
    URM_train, URM_test = dataset.get_URM_train_for_test_fold(n_test_fold=9)
    model = UserKNNCFRecommender(URM_train)
    model.fit()
    print("The recommendation for user 1 is: {}".format(model.recommend(1, cutoff=10)))
