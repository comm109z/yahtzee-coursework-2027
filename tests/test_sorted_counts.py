from helper_functions import *

def test_sorted_counts_varied_distribution():
    data = ["apple", "banana", "apple", "cherry", "cherry", "cherry"]
    assert sorted_counts(data) == [3, 2, 1] 

def test_sorted_counts_single_value():
    data = [42, 42, 42, 42]
    assert sorted_counts(data) == [4]

def test_sorted_counts_empty_list():
    data = []
    assert sorted_counts(data) == []

