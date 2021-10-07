# TensorBot
![](meta/tensor(glow).png)
This is a GUI based chatbot made with `tensorflow` and `PyQt5`. This also have speech recognisation implemented with `speech-recognisation` library.

## How to setup

1. Start by cloning the repository.
2. Install all the libraries that are there in requirements.txt
3. Train the chatbot, go to `train.ipynb`
4. Run `app.py`

To setup speech recognisation:

1. You have to create an azure account.
2. To get the API key, go to the [Microsoft Azure Portal Resources](https://portal.azure.com/) page, go to All `Resources` > `Add` > `See` `All` > Search `Speech` > `Create`, and fill in the form to make a "Speech" resource. On the resulting page (which is also accessible from the "All Resources" page in the Azure Portal), go to the "Show Access Keys" page, which will have two API keys, either of which can be used for the key parameter.
3. Now go to `data/DataMake.py` and place your api key there and run it.

To setup database:\
The database will be automatically setuped when you run `DataMake.py`

## About this project

I am a student of class 12<sup>th</sup> who loves doing programming. I made this project as a IP Project given to me. To me this bot came out OKay, I guess I won't be taking any pull requests, but you can still make one, if I like your commits I will merge. Tho you can feel free to make issues, I would love to help/modify the files.