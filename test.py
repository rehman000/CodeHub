from profanity_check import predict, predict_prob

predict(['predict() takes an array and returns a 1 for each string if it is offensive, else 0.'])
# [0]

predict(['fuck you'])
# [1]

is_post_profane = predict(['fuck you'])

print(is_post_profane)

print(is_post_profane[0])