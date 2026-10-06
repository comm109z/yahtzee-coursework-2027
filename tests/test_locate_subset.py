from helper_functions import *

def test_locate_subset_all_targets_found():
    full_list = ["apple", "banana", "cherry", "apple"]
    targets = ["cherry", "apple", "apple"]
    assert locate_subset(full_list, targets) == [2, 0, 3]

def test_locate_subset_missing_target():
    full_list = [10, 20, 30, 40]
    targets = [10, 50]
    assert locate_subset(full_list, targets) is False

def test_locate_subset_not_enough_duplicates():
    full_list = [5, 10, 15, 0]
    targets = [5, 5, 10]
    assert locate_subset(full_list, targets) is False
    
def test_locate_subset_empty_targets():
    full_list = [1, 2, 3]
    targets = []
    assert locate_subset(full_list, targets) == []