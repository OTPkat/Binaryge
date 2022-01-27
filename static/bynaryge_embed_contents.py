from static.emojis import nodder
bynaryge_rules = "`Bynaryge` is  a 1vs1 game. At the start of a party, a random number `n` will be sampled and written on" \
                 " the match embed. Then you will take turns with your opponent submitting binary numbers on the embed via" \
                 " the `!bym <binary_snumber>`. The sum of all submitted numbers (including the inital sampled " \
                 "number `n`) has to not exceed 2n. The game ends when there are no valid moves left. The player that started" \
                 " to submit wins if the total amount of 1's that has been written is odd"


bynaryge_example = "Say the inital number sampled is `n=1110 = (14)`," \
                   " it is the **first** number written on the match embed. " \
                   "So it will look like: \n" \
                   "*** Embedd numbers ***\n" \
                   "```1110 ```\n" \
                   "***Current sum ***\n" \
                   "```14``` \n" \
                   "***Current amount of 1's*** \n" \
                   "```3```\n" \
                   f" Madge and Sadge take turns, madge starts and submits `1100 = 12`. " \
                   f"The match embedd updates to: \n" \
                   "***Embedd numbers ***\n" \
                   f"```1110 \n" \
                   f"1100 ```\n" \
                    "***Current sum ***\n" \
                   "```26``` \n" \
                   "***Current amount of 1's*** \n" \
                   "```5```\n" \
                    f"Now sadge can only play one or two. Say he plays `10=2`. The match embed updates to \n" \
                   "***Embedd numbers ***\n" \
                   f"```1110 \n" \
                   f"1100 \n" \
                   f"10 ```\n" \
                    "***Current sum ***\n" \
                   "```28``` \n" \
                   "***Current amount of 1's*** \n" \
                   "```6```\n" \
                   f"Now since the sum cannot exceed `2n = 2*14 = 28`, there are no valid move left." \
                   f"The amount of 1's being even, Sadge wins. \n" \


