# zero-shot-crime-detection

Code and data for the paper _Garbage in, garbage out: Zero-shot detection of crime using Large Language Models_

# Dataset

We provide a dataset of manual descriptions for a sample of 12 surveillance videos from 14 categories (13 crime categories + normal), resulting in a dataset of 168 surveillance video descriptions. These are available in `test_001_labels.txt`.

We also include automatically generated captions for videos (at 10 second intervals) using Generative Image-to-text Transformers (GIT), Large Language-and-Vision Assistant (LLaVA), and YOLOv8 + ByteTrack. These are provided in  `test_001_captions.txt`, `test_001_llava.txt`, `test_001_tracking.txt` respectively.

# Zero-shot classification

The `collect.py` script performs zero-shot classification using GPT-4. These scripts require setting your `OPENAI_API_KEY` environment and an account with GPT-4 API access.

``` 
python3 collect.py "output.csv" "test_001_labels.txt"
python3 collect.py "output_captions.csv" "test_001_captions.txt"
python3 collect.py "output_llava.csv" "test_001_llava.txt"
python3 collect.py "output_tracks.csv" "test_001_tracking.txt"
```

# Result Visualisation

We provide the notebook `crime_classification_analysis.ipynb` that generates a confusion matrix and computes overall classification accuracy for each approach.
