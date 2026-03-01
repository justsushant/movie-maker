I've added a complete Python 3.10 Setup Guide to the 
walkthrough.md
.

Here are the exact steps to set up and run the project using Python 3.10:

1. Create the Environment
Since Python 3.10 is available on your system via pyenv, run this command to create a dedicated virtual environment:

bash
# python3.10 -m venv .venv310

pyenv shell 3.10.17 && python3.10 -m venv .venv

2. Install Dependencies
Activate the new environment and install the verified versions of the required packages:

bash
source .venv/bin/activate
pip install kokoro==0.7.4 soundfile
3. Run the Pipeline
Now you can execute the script to generate your audio and MoviePy metadata:

bash
python tts_pipeline.py
What happens next?
When you run the script for the first time:

It will automatically download the Kokoro-v1.0 model weights (~300MB).
It will download the spaCy English model (en_core_web_sm) required for text processing.
It will generate 

output_moviepy.json
, which contains the precise word-level timestamps linked to sentences, perfectly formatted for your MoviePy rolling text effect.



Why the JSON we created solves this
To make a rolling effect in MoviePy, you need two pieces of information simultaneously:

The full sentence context: so you can draw the whole sentence on the screen at once.
The exact timing of each word inside it: so you know exactly when to highlight a specific word within that sentence.
The standard SRT format doesn't support this naturally. That's exactly why 

tts_pipeline.py
 exports the 

output_moviepy.json
 file. It's not just a word-level subtitle file; it's a hierarchical data structure.

Look at the JSON structure it generated:

json
{
    "sentence_text": "The novel concludes with Kautenya accepting...", // <-- Draw this on screen
    "start_time": 0.225,
    "end_time": 5.2625,
    "words": [
        {
            "text": "The ", // <-- Highlight this at t=0.225
            "start_time": 0.225,
            "end_time": 0.325
        },
        // ...
    ]
}
How MoviePy will use it (The Logic)
When you write your MoviePy script, the logic will look something like this:

MoviePy asks: "What should frame t=0.300 look like?"
Your script checks the JSON and finds the sentence where 0.300 falls between its start_time and end_time. (e.g., "The novel concludes...")
Your script then checks the "words" array inside that sentence to find which specific word is active at t=0.300. (e.g., It finds "The").
MoviePy draws the full "sentence_text", but applies a yellow highlight only to the word "The".