from scoring_functions import *

# run a check on the score_3_of_a_kind
# in this case when coded the correct result should be 25

mydice = [6,6,6,5,2]
result = score_3_of_a_kind(mydice)
print(f"running score_3_of_a_kind on {mydice} ... result is {result}")
