from static.emojis import nodder
bynaryge_rules = "`Bynaryge` is  a 1vs1 game. At the start of a party, a random number `n` will be sampled and written on" \
                 " the match embed. Then you will take turns with your opponent submitting binary numbers on the embed via" \
                 " the `!bym <binary_snumber>`. The sum of all submitted numbers (including the inital sampled " \
                 "number `n`) has to not exceed 2n. The game ends when there are no valid moves left. The player that started" \
                 "to submit wins if the total amount of 1's that has been written is odd"

bynaryge_example = "Say the inital number sampled is `n=1110 = (14)`, it is the **first** number written on the embed." \
                   " Remember that the sum of all the numbers on the embed has to not exceed 11100 (28). \n" \
                   f" Madge and Sadge take turns, madge starts and submits `1100`. Now the current sum is `14 + 12 = 26 = 11010`.\n" \
                    "At this point we have `n=1110` and `1100` so a total of 5 1's. Now sadge can only play one or two. Say he plays 2" \
                   " then the sum is `28 = 11100` and the series of numbers submitted with `n` is: \n" \
                    "1110 \n" \
                    "1100 \n " \
                    "10 \n" \
                    "That makes 6 1's written -> Madge looses as he started and the amount 1 is even"

