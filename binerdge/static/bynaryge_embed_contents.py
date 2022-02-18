bynaryge_rules = "`Binerdge` is  a 1vs1 game. At the start of a party, a random number `n` will be sampled and written on" \
                 " the match embed. Then you will take turns with your opponent submitting binary numbers on the embed via" \
                 " the `!bym <binary_snumber>`. The sum of all submitted numbers (including the inital sampled " \
                 "number `n`) has to not exceed 2n. The game ends when there are no valid moves left. The player that started" \
                 " to submit wins if the total amount of 1's that has been written is odd"


bynaryge_example = "<a:pepeJam:929537274293682226> and <a:NODDERS:929537274436272158>  start playing a match. " \
                   "Say the inital sampled number is `n = 1110 = 14`," \
                   " it is the **first** number written on the match embed. " \
                   "So the match embed will look like: \n" \
                   "\n " \
                   "*** Embedd numbers ***\n" \
                   "```1110 ```" \
                   "***Current sum ***\n" \
                   "```14```" \
                   "***Current amount of 1's*** \n" \
                   "```3```\n " \
                   f" <a:pepeJam:929537274293682226> and <a:NODDERS:929537274436272158> take turns, <a:pepeJam:929537274293682226> starts and submits `1100 = 12`. " \
                   f"The match embedd updates to: \n" \
                   "\n " \
                   "***Embedd numbers ***\n" \
                   f"```1110 \n" \
                   f"1100 ```" \
                    "***Current sum ***\n" \
                   "```26```" \
                   "***Current amount of 1's*** \n" \
                   "```5```" \
                   "\n " \
                   f"Now <a:NODDERS:929537274436272158> can only play one or two. Say he plays `10=2`. The match embed updates to \n" \
                   "\n " \
                   "***Embedd numbers ***\n" \
                   f"```1110 \n" \
                   f"1100 \n" \
                   f"10 ```" \
                    "***Current sum ***\n" \
                   "```28```" \
                   "***Current amount of 1's*** \n" \
                   "```6```" \
                   "\n " \
                   f"Now since the sum cannot exceed `2n = 2*14 = 28`, there are no valid moves left." \
                   f" The amount of 1's being even, <a:NODDERS:929537274436272158>  wins. \n" \


