from flask import Flask
from flask_censor import Censor # This is based on profanity filter ... 

'''
from profanity_filter import ProfanityFilter

pf = ProfanityFilter()


pf.censor("That's bullshit!")
# "That's ********!"

pf.censor_word('fuck')
# Word(uncensored='fuck', censored='****', original_profane_word='fuck')
'''

censor = Censor()
censor.set_censorchars('*')

User_string = str ( input() )



censored_string = censor.censor(User_string)

print(censored_string)