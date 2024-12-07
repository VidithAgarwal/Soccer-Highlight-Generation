# **⚽ SoccerNet Highlight Generator**

## **📖 Overview**
This project automates the creation of soccer match highlights by:
- Downloading match videos.
- Identifying key moments.
- Compiling highlight reels.

It uses **ResNet-50** for feature extraction and a custom **GRU model with an attention mechanism** for event classification. For a live demonstration, the model can be deployed using tools like Gradio for interactive exploration.

---

## **✨ Features**

### **1. Data Preparation**
- **Dataset Source**: Leverages the SoccerNet dataset, which includes match videos and JSON files with detailed annotations.
- **Clip Extraction**: Extracts 10-second clips around key moments. For example:
  - If a goal occurs at 20 minutes, a clip from 19:55 to 20:05 is saved in the **goals** folder.
- **Organized Training Data**: Creates labeled folders (e.g., `goals`, `fouls`, `corners`) for each action type.

---

### **2. Model Training**
- **Feature Extraction**: Converts 10-second clips into tensors using a pre-trained **ResNet-50** model.
- **Training Process**: 
  - Pairs feature tensors with labels (folder names).
  - Feeds them into a custom **GRU model with attention** for classification.
- **Fine-Tuning**: Optimizes the GRU model for precise event detection.
- **Output**: Produces a trained model that can identify soccer actions from video clips.

---

### **3. Action Detection**
- **Video Segmentation**: Divides full match videos into 10-second clips.
- **Action Classification**: Passes each clip through the trained model to classify actions (e.g., goal, foul, kickoff).
- **Action Ranking**: Assigns importance scores to actions based on predefined rankings.

---

### **4. Highlight Generation**
- **Key Moment Selection**: Identifies the most critical moments using rankings.
- **Highlight Compilation**: Stitches the clips into a smooth highlight reel.
- **Automated Workflow**: Generates highlight videos from full match footage, ready for sharing.

---

### **5. User Interaction**
- **Input**: Users upload a full soccer match video.
- **Output**: A polished highlight reel featuring the most exciting moments.

---

## **📂 Document Overview**
| File                          | Description                                           |
|-------------------------------|-------------------------------------------------------|
| `video_download.py`           | Downloads match videos from the SoccerNet server.     |
| `label_extraction.py`         | Extracts key timestamps and creates video clips.      |
| `resnet50_feature_extraction.py` | Extracts feature vectors using ResNet-50.          |
| `model_training.py`           | Trains the GRU model with attention.                 |
| `inference_on_all_videos.py`  | Evaluates the model's performance.                   |
| `test_video_to_clips.py`      | Segments full match videos into 10-second clips.     |
| `highlight_generator.py`      | Compiles highlights from classified clips.           |

---

## **🚀 Getting Started**

### **Prerequisites**
Ensure you have the following installed:
- Python 3.8+
- PyTorch
- OpenCV
- torchvision
- NumPy

---

### **Installation**

### Step 1: Clone the Repository
```bash
git clone https://github.com/aatmaj28/Soccer-Highlight-Generation.git
cd Soccer-Highlight-Generation
```

### Step 2: Install Dependencies
Install the required Python packages:
```bash
pip install <all packages mentioned above>
```

### Step 3: Download Videos
Run the video download script:
```bash
python video_download.py
```

### Step 4: Extract Key Moments from videos into clips
```bash
python label_extraction.py
```

### Step 5: Extract Features into feature vector
```bash
python resnet50_feature_extraction.py
```

### Step 6: Train the Model
Train the GRU model using the prepared dataset:
```bash
python model_training.py
```

### Step 7: Evaluate the Model
Run `inference_on_all_videos.py` to test model performance:
```bash
python inference_on_all_videos.py
```

### Step 8: Generate Highlights
Use the trained model to create a highlight reel:
```bash
python test_video_to_clips.py
python highlight_generation.py
```

## **Contributing**
Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request.

---

## **Acknowledgments**
This project utilizes the following resources and libraries:
- [PyTorch](https://pytorch.org/) for deep learning models.
- [OpenCV](https://opencv.org/) for video processing.
- [SoccerNet](https://www.soccer-net.org/) for providing video data and annotations.
- Pre-trained **ResNet-50** for feature extraction.

---

## **Resources**
The models were trained using and combining the following resources:
- [SoccerNet datasets](https://www.soccer-net.org/) for annotated match videos.
- Custom-built datasets with enhanced event annotations.
