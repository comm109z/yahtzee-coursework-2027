from helper_functions import *
from yahtzee_backend import *

# run a check on the sorted_counts
# in this case when coded the correct result should be [3,2,1]

data = ["apple", "banana", "apple", "cherry", "cherry", "cherry"]
result = sorted_counts(data)
print(f"running sorted_counts on {data}"
print(f"result is {result}")

# run a check on the score_3_of_a_kind
# in this case when coded the correct result should be 25

mydice = [6,6,6,5,2]
result = score_3_of_a_kind(mydice)
print(f"running score_3_of_a_kind on {mydice} ... result is {result}")
