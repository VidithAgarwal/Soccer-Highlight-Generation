# AI-Powered Soccer Video Highlight Generation

## Overview
This project is an **Automatic Video Highlight Generation System** that processes full soccer match footage to identify and compile key moments into a cohesive highlight reel. By leveraging deep learning models, the system detects and ranks crucial events such as goals, fouls, shots, saves, and other noteworthy actions. It automates the time-consuming process of creating highlight videos, offering fans, coaches, and analysts an efficient way to view match summaries.

## Features
- **Action Detection and Classification**: Recognizes key soccer actions like goals, fouls, corner kicks, offsides, and saves.
- **Event Scoring and Ranking**: Prioritizes key moments based on importance (e.g., goals > fouls) and audience preferences.
- **Video Segmentation**: Extracts 20-second clips around detected events for seamless highlight compilation.
- **Automatic Highlight Compilation**: Arranges clips chronologically or by priority with smooth transitions.
- **Customization**: Allows users to define the duration and priority of events in the generated highlights.

## How It Works
1. **Data Preparation**:
   - Utilized the **Soccernet Dataset**, which provides full match videos and JSON annotations for key events.
   - A script extracts 20-second video clips around each key event (e.g., 19:50 - 20:10 for a goal) and organizes them into labeled folders (e.g., `goals`, `fouls`).

2. **Model Training**:
   - **Feature Extraction**: Used **ResNet** to convert video frames into tensors.
   - **Action Recognition**: Paired the tensors with their corresponding labels and trained a fine-tuned **GRU model** to classify actions.
   - **Supervised Learning**: Trained the model using the labeled 20-second video clips.

3. **Highlight Generation**:
   - The system breaks a full match into 20-second video clips.
   - Each clip is passed through the trained model to classify the action occurring.
   - Clips containing key actions are ranked based on predefined importance and stitched into a highlight reel.

4. **Output**:
   - Generates a smooth, compact highlight reel, tailored to user-defined preferences for duration and event focus.

## Tech Stack
- **Programming Language**: Python
- **Libraries/Frameworks**: 
  - TensorFlow/Keras (Deep Learning)
  - OpenCV (Video Processing)
  - ResNet (Feature Extraction)
  - GRU (Action Recognition)
- **Dataset**: Soccernet (Soccer matches with JSON annotations)
- **Other Tools**: JSON (Annotation Parsing)

## Directory Structure

```bash
project/
├── videos/
│   ├── league_name/           # Name of the league. Eg. england_epl
|       ├── Season             # The season. Eg. 2015-2026
|         ├── Match            # Folder with name of the match. Eg. 2015-02-21 - 18-00 Chelsea 1 - 1 Burnley
|            ├── 1st Half      # First half of the match (45 mins clip). Named 1_720p.
|            ├── 2nd Half      # Second half of the match (45 mins clip). Named 2_720p.
|            ├── Json file     # Labels.json file containing the annotation for this particular match
│   ├── extracted/             # Extracted key moments 
│       ├── goals/             # Clips labeled as goals
│       ├── fouls/             # Clips labeled as fouls
│       ├── saves/             # Clips labeled as saves
├── /
│   ├── ResNet and GRU         # Implementation of ResNet and GRU model
│   ├── Data_gen_script        # Script to extract 20sec labeled videos
│   ├── Feature_Extraction.py  # Script to extract features from videos
|   ├── Video_Download.py      # Script to download the full match videos
├── README.md                  # Project documentation
└── requirements.txt           # List of dependencies
```
## Setup and Usage

### 1. Prerequisites
- Python 3.8 or above
- Install required dependencies:  
  ```bash
  pip install -r requirements.txt
   ```
### 2. Dataset Setup
- To Download the Soccernet Dataset run the `Video_Download script`. It will automatically create the videos directory with the videos.
```bash
python Video_Download.py
```
### 3. Extract Clips and place them in their respective folder

- Run the script file `Data_gen_script` to extract the 20 second clips of key moments from full videos based on the annotation and store them in their respective folder.
```bash
python Data_gen_script.py
```
### 4. Convert the data into tensors and pass them into GRU for training.

- Run the FAI Project ResNet and GRU Implementation.ipynb file to first trigger ResNet to extract features and convert clips into tensors, which is then passed to the fine-tuned GRU model for training.


## Future Improvements
- **Real-Time Processing**: Extend the system to support real-time action detection during live matches.
- **Multi-Sport Support**: Adapt the model for other sports like basketball, cricket, and tennis.
- **Improved Accuracy**: Experiment with transformers and hybrid models to enhance classification precision.

## Acknowledgments
- **Soccernet Dataset** for providing the match videos and annotations.
- **TensorFlow/Keras and ResNet** for enabling robust deep learning workflows.
