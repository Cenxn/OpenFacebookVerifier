# OpenFacebookVerifier
This is a script to validate LLM generated code based on [Facebook Infer](https://github.com/facebook/infer) implementation.

[Demo_1: NO API Setting](https://drive.google.com/file/d/1x8mGVQbVhWuUcWsq83j1VpdTWdPYbmWW/view?usp=sharing) [Demo_2: With API Setting](https://drive.google.com/file/d/19CxoHW1vdUkwQbTjCFg4j42bkjNLUkQZ/view?usp=sharing)

(Optional)Set up an .env file before executing, but of course if you don't set up an `.env` file you can use this script normally, but you will lose some specific functionality.
``` bash
# Once you add your API key below, make sure to not share it with anyone! The API key should remain private.
OPENAI_API_KEY=<your_key>
```
Install the docker via
``` bash
docker build -t comp0103infer .
```
If you did not construct the OpenAI API key, you could then execute the script via 
```
docker run -it comp0103infer /bin/bash
cd /OpenFacebookVerifier/
python3 main.py
```
If you construct the OpenAI API key in the `.env` file, you could execute the script via
``` bash
docker run --rm -it --env-file ./path/to/your/.env comp0103infer
cd /OpenFacebookVerifier/
python3 main.py
```
