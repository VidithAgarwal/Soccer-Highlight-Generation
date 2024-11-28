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

```markdown
project/ │ ├── data/ │ ├── raw_videos/ # Full match videos │ ├── annotations/ # JSON files with event details │ ├── processed_clips/ # 20-second labeled video clips │ ├── goals/ │ ├── fouls/ │ ├── saves/ │ ├── scripts/ │ ├── preprocess.py # Script to extract labeled clips │ ├── train_model.py # Script to train the ResNet + GRU model │ ├── generate_highlights.py # Script to generate highlight reels │ ├── models/ │ ├── resnet/ # Pretrained ResNet model for feature extraction │ ├── gru/ # Fine-tuned GRU model for action recognition │ ├── output/ │ ├── highlights/ # Generated highlight reels │ ├── README.md # Project documentation └── requirements.txt # List of dependencies
