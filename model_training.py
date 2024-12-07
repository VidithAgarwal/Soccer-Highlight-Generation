# -*- coding: utf-8 -*-
"""model_training.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15g-haBi508k29h0Y39eIjEQMTaKGbvmR

# Training Loop using Attention Mechanism (Attempting to focus on important frames)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import os

# Define the device based on CUDA availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Define an Attention-Enhanced GRU model
class AttentionEnhancedGRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=3, dropout=0.3):
        super(AttentionEnhancedGRUModel, self).__init__()

        # GRU Layers with Attention Mechanism
        self.gru = nn.GRU(input_size, hidden_size, num_layers=num_layers,
                          batch_first=True, dropout=dropout)

        # Attention Mechanism
        self.attention_layer = nn.Linear(hidden_size, 1)

        # Fully Connected Layers for Classification
        self.fc_classification = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, output_size)
        )

        # Confidence Score Layer
        self.fc_confidence = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()  # Outputs a confidence score between 0 and 1
        )

    def forward(self, x):
        # GRU processing
        gru_out, _ = self.gru(x)

        # Attention Mechanism
        attention_weights = F.softmax(self.attention_layer(gru_out), dim=1)
        context_vector = torch.sum(gru_out * attention_weights, dim=1)

        # Classification Output
        classification_output = self.fc_classification(context_vector)

        # Confidence Score Output
        confidence_score = self.fc_confidence(context_vector)

        return {
            'classification': classification_output,
            'confidence': confidence_score,
            'attention_weights': attention_weights
        }

# Prepare model function
def prepare_model(input_size, hidden_size, output_size):
    model = AttentionEnhancedGRUModel(
        input_size=input_size,
        hidden_size=hidden_size,
        output_size=output_size
    ).to(device)
    return model

# Inference function
def predict(model, input_data):
    model.eval()
    with torch.no_grad():
        outputs = model(input_data)

        # Softmax for class probabilities
        class_probs = F.softmax(outputs['classification'], dim=1)
        predicted_class = torch.argmax(class_probs, dim=1)

        return {
            'predicted_class': predicted_class,
            'class_probabilities': class_probs,
            'confidence_score': outputs['confidence'],
            'attention_weights': outputs['attention_weights']
        }

# Modified training loop
def train_model(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0

    for features_batch, labels_batch in dataloader:
        features_batch, labels_batch = features_batch.to(device), labels_batch.to(device)

        optimizer.zero_grad()

        # Forward pass
        outputs = model(features_batch)

        # Calculate classification loss
        classification_loss = criterion(outputs['classification'], labels_batch)

        # Optional: Add confidence loss
        confidence_loss = F.binary_cross_entropy(
            outputs['confidence'].squeeze(),
            (outputs['classification'].argmax(1) == labels_batch).float()
        )

        # Combined loss
        total_batch_loss = classification_loss + 0.1 * confidence_loss

        total_batch_loss.backward()
        optimizer.step()

        total_loss += total_batch_loss.item()

    return total_loss

# Load the previously extracted features
features_path = r'D:\\FAI Project\\FAI_Data_Final\\extracted_features2.5TR.pt'
loaded_data = torch.load(features_path)

# Extract features and labels
all_features = loaded_data['features']
all_labels = loaded_data['labels']
label_to_index = loaded_data['label_to_index']
unique_labels = loaded_data['unique_labels']

# Print some information about the dataset
print("Loaded Features Shape:", all_features.shape)
print("Loaded Labels Shape:", all_labels.shape)
print("Unique Labels:", unique_labels)
print("Label to Index Mapping:", label_to_index)

# Hyperparameters
input_size = all_features.shape[2]  # Feature vector size
hidden_size = 2048  # Increased hidden size for better representation
output_size = len(unique_labels)  # Set output size based on the number of unique labels
num_epochs = 50  # Increased epochs for potentially better training
batch_size = 16  # Adjusted batch size
learning_rate = 0.0001

# Prepare the dataset and dataloader
dataset = TensorDataset(all_features, all_labels)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Instantiate the model, loss function, and optimizer
model = prepare_model(input_size, hidden_size, output_size)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Training loop with validation tracking
best_loss = float('inf')
for epoch in range(num_epochs):
    total_loss = train_model(model, dataloader, criterion, optimizer, device)

    # Calculate average loss for the epoch
    avg_loss = total_loss / len(dataloader)
    print(f'Epoch [{epoch + 1}/{num_epochs}], Average Loss: {avg_loss:.4f}')

    # Save the best model
    if avg_loss < best_loss:
        best_loss = avg_loss
        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': best_loss,
            'label_to_index': label_to_index,
            'unique_labels': unique_labels,
            'input_size': input_size,
            'output_size': output_size
        }, 'best_attention_enhanced_gru_model.pth')
        print(f"Best model saved with loss: {best_loss:.4f}")

# Final model save
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': best_loss,
    'label_to_index': label_to_index,
    'unique_labels': unique_labels,
    'input_size': input_size,
    'output_size': output_size
}, 'final_attention_enhanced_gru_model.pth')

print("Training completed. Models saved.")

"""# Training Loop using the .pt files (Initial Architecture)"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import os
import matplotlib.pyplot as plt

# Define the device based on CUDA availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Define an enhanced GRU model with more layers and dropout
class EnhancedGRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=3, dropout=0.3):
        super(EnhancedGRUModel, self).__init__()

        # Add multiple GRU layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers=num_layers, batch_first=True, dropout=dropout)

        # Fully connected layers with increased hidden size
        self.fc1 = nn.Linear(hidden_size, hidden_size * 2)  # Increase the size of the first FC layer
        self.fc2 = nn.Linear(hidden_size * 2, hidden_size)  # Keep the second layer the same size
        self.fc3 = nn.Linear(hidden_size, output_size)  # Final output layer
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)  # Dropout layer

    def forward(self, x):
        out, _ = self.gru(x)
        out = out[:, -1, :]  # Take the output from the last time step
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)  # Apply dropout
        out = self.fc2(out)
        out = self.relu(out)
        out = self.dropout(out)  # Apply dropout again
        return self.fc3(out)

# Load the previously extracted features
features_path = r'D:\\FAI Project\\FAI_Data_Final\\extracted_features2.5TR.pt'
loaded_data = torch.load(features_path)

# Extract features and labels
all_features = loaded_data['features']
all_labels = loaded_data['labels']
label_to_index = loaded_data['label_to_index']
unique_labels = loaded_data['unique_labels']

# Print some information about the dataset
print("Loaded Features Shape:", all_features.shape)
print("Loaded Labels Shape:", all_labels.shape)
print("Unique Labels:", unique_labels)
print("Label to Index Mapping:", label_to_index)

# Hyperparameters
input_size = all_features.shape[2]  # Feature vector size
hidden_size = 2048  # Increased hidden size for better representation
output_size = len(unique_labels)  # Set output size based on the number of unique labels
num_epochs = 50  # Increased epochs for potentially better training
batch_size = 16  # Adjusted batch size
learning_rate = 0.0001
validation_split = 0.2  # 20% of data for validation

# Split the dataset into training and validation sets
total_size = len(all_features)
val_size = int(total_size * validation_split)
train_size = total_size - val_size

# Create datasets and dataloaders
full_dataset = TensorDataset(all_features, all_labels)
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

# Instantiate the model, loss function, and optimizer
model = EnhancedGRUModel(input_size, hidden_size, output_size).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Lists to store loss values for plotting
train_losses = []
val_losses = []

# Training loop with validation tracking
best_loss = float('inf')
for epoch in range(num_epochs):
    # Training phase
    model.train()
    total_train_loss = 0

    for features_batch, labels_batch in train_loader:
        # Move data to GPU
        features_batch, labels_batch = features_batch.to(device), labels_batch.to(device)

        # Zero gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(features_batch)

        # Calculate loss
        loss = criterion(outputs, labels_batch)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        total_train_loss += loss.item()

    # Validation phase
    model.eval()
    total_val_loss = 0
    with torch.no_grad():
        for features_batch, labels_batch in val_loader:
            # Move data to GPU
            features_batch, labels_batch = features_batch.to(device), labels_batch.to(device)

            # Forward pass
            outputs = model(features_batch)

            # Calculate validation loss
            val_loss = criterion(outputs, labels_batch)
            total_val_loss += val_loss.item()

    # Calculate average losses
    avg_train_loss = total_train_loss / len(train_loader)
    avg_val_loss = total_val_loss / len(val_loader)

    # Store losses for plotting
    train_losses.append(avg_train_loss)
    val_losses.append(avg_val_loss)

    print(f'Epoch [{epoch + 1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Validation Loss: {avg_val_loss:.4f}')

    # Save the best model
    if avg_val_loss < best_loss:
        best_loss = avg_val_loss
        torch.save({
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': best_loss,
            'label_to_index': label_to_index,
            'unique_labels': unique_labels,
            'input_size': input_size,
            'output_size': output_size
        }, 'best_enhanced_gru_model.pth')
        print(f"Best model saved with validation loss: {best_loss:.4f}")

# Final model save
torch.save({
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': best_loss,
    'label_to_index': label_to_index,
    'unique_labels': unique_labels,
    'input_size': input_size,
    'output_size': output_size
}, 'final_enhanced_gru_model.pth')

print("Training completed. Models and loss plot saved.")

"""# Predition on a Single Test video using the Saved Model"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import numpy as np
import torchvision.models as models

# Attention-Enhanced GRU Model
class AttentionEnhancedGRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=3, dropout=0.3):
        super(AttentionEnhancedGRUModel, self).__init__()

        # GRU Layers with Attention Mechanism
        self.gru = nn.GRU(input_size, hidden_size, num_layers=num_layers,
                          batch_first=True, dropout=dropout)

        # Attention Mechanism
        self.attention_layer = nn.Linear(hidden_size, 1)

        # Fully Connected Layers for Classification
        self.fc_classification = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, output_size)
        )

        # Confidence Score Layer
        self.fc_confidence = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()  # Outputs a confidence score between 0 and 1
        )

    def forward(self, x):
        # Ensure input is 3D (batch, sequence, features)
        if x.dim() == 4:
            # If 4D, reshape to flatten spatial dimensions
            x = x.view(x.size(0), x.size(1), -1)

        # GRU processing
        gru_out, _ = self.gru(x)

        # Attention Mechanism
        attention_weights = F.softmax(self.attention_layer(gru_out), dim=1)
        context_vector = torch.sum(gru_out * attention_weights, dim=1)

        # Classification Output
        classification_output = self.fc_classification(context_vector)

        # Confidence Score Output
        confidence_score = self.fc_confidence(context_vector)

        return {
            'classification': classification_output,
            'confidence': confidence_score,
            'attention_weights': attention_weights
        }

def extract_features(video_clip, device):
    # Load ResNet model for feature extraction
    resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT).to(device)
    resnet.eval()

    frames = []
    cap = cv2.VideoCapture(video_clip)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (224, 224))
        frame = frame / 255.0
        frames.append(frame)
    cap.release()

    frames = np.array(frames)
    feature_vectors = []
    with torch.no_grad():
        for frame in frames:
            # Move input tensor to GPU
            input_tensor = torch.tensor(frame).permute(2, 0, 1).unsqueeze(0).float().to(device)
            feature = resnet(input_tensor)
            # Move feature back to CPU for numpy conversion
            feature_vectors.append(feature.cpu().numpy())
    return np.array(feature_vectors)

def predict_video(video_path, model_path):
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load the saved model checkpoint
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)

    # Recreate the model with the same architecture
    model = AttentionEnhancedGRUModel(
        input_size=checkpoint['input_size'],
        hidden_size=2048,
        output_size=checkpoint['output_size']
    ).to(device)

    # Load the model weights
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    # Extract features from the video
    features = extract_features(video_path, device)

    # Convert features to tensor and move to device
    features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(device)

    # Perform prediction
    with torch.no_grad():
        outputs = model(features_tensor)

        # Softmax for class probabilities
        class_probs = F.softmax(outputs['classification'], dim=1)
        predicted_class = torch.argmax(class_probs, dim=1)
        confidence_score = outputs['confidence']

    # Retrieve the original label mapping
    label_to_index = checkpoint['label_to_index']
    unique_labels = checkpoint['unique_labels']

    # Convert numeric prediction back to original label
    index_to_label = {index: label for label, index in label_to_index.items()}
    predicted_label = index_to_label[predicted_class.item()]

    # Print prediction details
    print("\nPrediction Results:")
    print(f"Video Path: {video_path}")
    print(f"Predicted Label: {predicted_label}")
    print(f"Confidence Score: {confidence_score.item():.4f}")
    print("\nProbabilities:")
    for label, prob in zip(unique_labels, class_probs.cpu().numpy()[0]):
        print(f"{label}: {prob:.4f}")

    return predicted_label, class_probs.cpu().numpy()[0], confidence_score.item()

# Example usage
if __name__ == "__main__":
    # Path to your saved model (use the path where you saved the model)
    model_path = 'best_attention_enhanced_gru_model.pth'

    # Path to the video you want to predict
    video_path = r'nothing_half_2_pos_1869533_idx_161.mp4'

    # Perform prediction
    predicted_label, probabilities, confidence = predict_video(video_path, model_path)

"""# Final Stitching Logic by taking the Big Video as the input (Options - 3/5 min highlight)"""

import os
import torch
import torch.nn as nn
import cv2
import numpy as np
from torchvision import transforms
from torchvision.models import resnet50
import torch.nn.functional as F
from collections import Counter
import itertools

class EnhancedGRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=3, dropout=0.3):
        super(EnhancedGRUModel, self).__init__()

        self.feature_reducer = nn.Linear(input_size, 1000)  # Reduce features to 1000

        self.gru = nn.GRU(1000, hidden_size, num_layers=num_layers, batch_first=True, dropout=dropout)

        self.fc1 = nn.Linear(hidden_size, hidden_size * 2)
        self.fc2 = nn.Linear(hidden_size * 2, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Reduce feature dimensions
        x = self.feature_reducer(x)

        out, _ = self.gru(x)
        out = out[:, -1, :]
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.dropout(out)
        return self.fc3(out)

class HighlightGenerator:
    def __init__(self, model_path='final_enhanced_gru_model.pth'):
        # Rankings dictionary
        self.rankings = {
           "Shots on target": 1, "Red card": 2,
            "Corner": 3, "Yellow card": 4, "Shots off target": 5,
            "Foul": 6, "Direct free-kick": 7, "Offside": 8
        }

        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the model with weights_only=True
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)

        # Model parameters
        input_size = 2048  # ResNet feature size
        hidden_size = 2048
        output_size = checkpoint['output_size']

        # Initialize model
        self.model = EnhancedGRUModel(input_size, hidden_size, output_size).to(self.device)

        # Load state dict with strict=False to ignore missing keys
        self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)
        self.model.eval()

        # Store label mapping
        self.label_to_index = checkpoint['label_to_index']
        self.index_to_label = {v: k for k, v in self.label_to_index.items()}

        # ResNet feature extractor
        resnet = resnet50(pretrained=True)
        self.feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
        self.feature_extractor.to(self.device)
        self.feature_extractor.eval()

        # Image transformations
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def extract_features(self, video_path):
        """Extract features from video clips"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        clip_duration = 20  # seconds
        clip_frames = int(fps * clip_duration)

        video_features = []
        video_clips = []
        clip_labels = []

        frame_count = 0
        current_clip = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_clip.append(frame)
            frame_count += 1

            # When clip is full or video ends
            if len(current_clip) == clip_frames:
                # Convert clip to features
                clip_tensor = self.process_clip(current_clip)
                video_features.append(clip_tensor)
                video_clips.append(current_clip)

                # Reset clip
                current_clip = []

        # Handle last incomplete clip if exists
        if current_clip:
            # Pad the clip to match the expected length
            while len(current_clip) < clip_frames:
                current_clip.append(current_clip[-1])  # Repeat last frame

            clip_tensor = self.process_clip(current_clip)
            video_features.append(clip_tensor)
            video_clips.append(current_clip)

        cap.release()

        return video_features, video_clips

    def process_clip(self, clip):
        """Process a video clip to extract features"""
        clip_features = []
        for frame in clip:
            # Convert to tensor and extract features
            input_tensor = self.transform(frame).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.feature_extractor(input_tensor)
                clip_features.append(features.squeeze().cpu().numpy())

        return torch.tensor(clip_features).float().unsqueeze(0)

    def predict_highlights(self, video_features):
        """Predict highlights for each clip"""
        predictions = []
        with torch.no_grad():
            for features in video_features:
                features = features.to(self.device)
                output = self.model(features)
                prob = F.softmax(output, dim=1)
                pred = torch.argmax(prob, dim=1).item()
                predicted_label = self.index_to_label[pred]
                predictions.append(predicted_label)
                print(f"Predicted label for the clip: {predicted_label}")  # Print predicted label for each clip

        return predictions

    def create_highlights(self, video_path, highlight_duration_minutes):
        """
        Generate highlights with a specific stitching strategy:
        1. Start with a Kick-off clip
        2. Distribute Goal clips sequentially throughout the video
        3. Add other clips based on ranking
        """
        # Extract features and predict labels
        video_features, video_clips = self.extract_features(video_path)
        predictions = self.predict_highlights(video_features)

        # Group clips by label
        labeled_clips = {}
        for label, clip in zip(predictions, video_clips):
            if label not in labeled_clips:
                labeled_clips[label] = []
            labeled_clips[label].append(clip)

        # Sort labels by ranking
        sorted_labels = sorted(self.rankings.keys(), key=lambda x: self.rankings[x])

        # Prepare final highlight clips
        highlight_clips = []
        total_duration = 0
        max_duration = highlight_duration_minutes * 60

        # Get video capture details
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        clip_duration = len(video_clips[0]) / fps
        cap.release()

        # Strategy for clip selection and sequential placement

        # 1. Start with a Kick-off clip if available
        if "Kick-off" in labeled_clips and labeled_clips["Kick-off"]:
            highlight_clips.append(labeled_clips["Kick-off"].pop(0))
            total_duration += clip_duration

        # Prepare Goal clips for sequential insertion
        goal_clips = labeled_clips.get("Goal", [])

        # Tracking clip order for goal insertion
        label_clip_counts = {label: 0 for label in self.rankings.keys()}

        # Add clips to fill the highlight duration
        while total_duration < max_duration:
            for label in sorted_labels:
                # Skip if we've reached max duration
                if total_duration >= max_duration:
                    break

                # Special handling for Goal clips
                if label == "Goal":
                    # If goal clips are available, insert them sequentially
                    if goal_clips:
                        highlight_clips.append(goal_clips.pop(0))
                        total_duration += clip_duration
                        continue

                # Add clips for other labels
                if label in labeled_clips and labeled_clips[label]:
                    highlight_clips.append(labeled_clips[label].pop(0))
                    total_duration += clip_duration
                    label_clip_counts[label] += 1

        # Video writing process
        output_path = f'highlights_{highlight_duration_minutes}min.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Create video writer
        out = cv2.VideoWriter(output_path, fourcc, fps,
                               (highlight_clips[0][0].shape[1], highlight_clips[0][0].shape[0]))

        # Stitch clips together by writing frames
        for clip in highlight_clips:
            for frame in clip:
                out.write(frame)

        out.release()

        return output_path

def main():
    # Get video path from user
    video_path = 'Test_video_LowRes_Small.mp4'

    # Validate video path
    if not os.path.exists(video_path):
        print("Invalid video path. Please check and try again.")
        return

    # Ask for highlight duration
    while True:
        try:
            duration = int(input("How many minutes of highlights do you want? (3/5): "))
            if duration in [3, 5]:
                break
            else:
                print("Please choose 3 or 5 minutes.")
        except ValueError:
            print("Please enter a valid number.")

    # Generate highlights
    generator = HighlightGenerator()
    output_video = generator.create_highlights(video_path, duration)

    print(f"Highlights generated successfully: {output_video}")

if __name__ == "__main__":
    main()

import os
import torch
import torch.nn as nn
import cv2
import numpy as np
from torchvision import transforms
from torchvision.models import resnet50
import torch.nn.functional as F
from collections import Counter
import itertools

class AttentionEnhancedGRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=3, dropout=0.3, use_feature_reducer=True):
        super(AttentionEnhancedGRUModel, self).__init__()

        # Optional feature reducer
        self.use_feature_reducer = use_feature_reducer
        if use_feature_reducer:
            self.feature_reducer = nn.Linear(input_size, 1000)
            gru_input_size = 1000
        else:
            gru_input_size = input_size

        # GRU Layers with Attention Mechanism
        self.gru = nn.GRU(gru_input_size, hidden_size, num_layers=num_layers,
                          batch_first=True, dropout=dropout)

        # Attention Mechanism
        self.attention_layer = nn.Linear(hidden_size, 1)

        # Fully Connected Layers for Classification
        self.fc_classification = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, output_size)
        )

        # Confidence Score Layer
        self.fc_confidence = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()  # Outputs a confidence score between 0 and 1
        )

    def forward(self, x):
        # Optional feature reduction
        if self.use_feature_reducer:
            x = self.feature_reducer(x)

        # GRU processing
        gru_out, _ = self.gru(x)

        # Attention Mechanism
        attention_weights = F.softmax(self.attention_layer(gru_out), dim=1)
        context_vector = torch.sum(gru_out * attention_weights, dim=1)

        # Classification Output
        classification_output = self.fc_classification(context_vector)

        # Confidence Score Output
        confidence_score = self.fc_confidence(context_vector)

        return {
            'classification': classification_output,
            'confidence': confidence_score,
            'attention_weights': attention_weights
        }

class HighlightGenerator:
    def __init__(self, model_path='final_attention_enhanced_gru_model.pth'):
        # Rankings dictionary
        self.rankings = {
           "Shots on target": 1, "Red card": 2,
            "Corner": 3, "Yellow card": 4, "Shots off target": 5,
            "Foul": 6, "Direct free-kick": 7, "Offside": 8
        }

        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the model checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)

        # Model parameters
        input_size = 2048  # ResNet feature size
        hidden_size = 2048
        output_size = checkpoint['output_size']

        # Initialize model with flexible feature reducer
        self.model = AttentionEnhancedGRUModel(
            input_size,
            hidden_size,
            output_size,
            use_feature_reducer=True
        ).to(self.device)

        # Load state dict with partial loading
        model_dict = self.model.state_dict()
        checkpoint_dict = checkpoint['model_state_dict']

        # Only load matching keys
        pretrained_dict = {k: v for k, v in checkpoint_dict.items() if k in model_dict}
        model_dict.update(pretrained_dict)

        # Load the updated state dictionary
        self.model.load_state_dict(model_dict)
        self.model.eval()

        # Store label mapping
        self.label_to_index = checkpoint['label_to_index']
        self.index_to_label = {v: k for k, v in self.label_to_index.items()}

        # ResNet feature extractor
        resnet = resnet50(weights='IMAGENET1K_V1')
        self.feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
        self.feature_extractor.to(self.device)
        self.feature_extractor.eval()

        # Image transformations
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def extract_features(self, video_path):
        """Extract features from video clips"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        clip_duration = 20  # seconds
        clip_frames = int(fps * clip_duration)

        video_features = []
        video_clips = []

        frame_count = 0
        current_clip = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_clip.append(frame)
            frame_count += 1

            # When clip is full or video ends
            if len(current_clip) == clip_frames:
                # Convert clip to features
                clip_tensor = self.process_clip(current_clip)
                video_features.append(clip_tensor)
                video_clips.append(current_clip)

                # Reset clip
                current_clip = []

        # Handle last incomplete clip if exists
        if current_clip:
            # Pad the clip to match the expected length
            while len(current_clip) < clip_frames:
                current_clip.append(current_clip[-1])  # Repeat last frame

            clip_tensor = self.process_clip(current_clip)
            video_features.append(clip_tensor)
            video_clips.append(current_clip)

        cap.release()

        return video_features, video_clips

    def process_clip(self, clip):
        """Process a video clip to extract features"""
        clip_features = []
        for frame in clip:
            # Convert to tensor and extract features
            input_tensor = self.transform(frame).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.feature_extractor(input_tensor)
                clip_features.append(features.squeeze().cpu().numpy())

        return torch.tensor(clip_features).float().unsqueeze(0)

    def predict_highlights(self, video_features):
        """Predict highlights for each clip with confidence"""
        predictions = []
        confidences = []

        with torch.no_grad():
            for features in video_features:
                features = features.to(self.device)
                output = self.model(features)

                # Get class probabilities
                prob = F.softmax(output['classification'], dim=1)
                pred = torch.argmax(prob, dim=1).item()

                predicted_label = self.index_to_label[pred]
                confidence_score = output['confidence'].item()

                predictions.append(predicted_label)
                confidences.append(confidence_score)

                print(f"Predicted label: {predicted_label}, Confidence: {confidence_score:.2f}")

        return predictions, confidences

    def create_highlights(self, video_path, highlight_duration_minutes):
        """
        Generate highlights with confidence-based selection
        """
        # Extract features and predict labels with confidence
        video_features, video_clips = self.extract_features(video_path)
        predictions, confidences = self.predict_highlights(video_features)

        # Group clips by label with confidence tracking
        labeled_clips = {}
        for label, clip, conf in zip(predictions, video_clips, confidences):
            if label not in labeled_clips:
                labeled_clips[label] = []
            labeled_clips[label].append((clip, conf))

        # Sort labels by ranking and confidence
        sorted_labels = sorted(self.rankings.keys(), key=lambda x: (self.rankings[x], -sum(conf for _, conf in labeled_clips.get(x, []))))

        # Prepare final highlight clips
        highlight_clips = []
        total_duration = 0
        max_duration = highlight_duration_minutes * 60

        # Get video capture details
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        clip_duration = len(video_clips[0]) / fps
        cap.release()

        # Strategy for clip selection with confidence
        # 1. Start with highest-confidence Goal clip if available
        goal_clips = sorted(labeled_clips.get("Goal", []), key=lambda x: x[1], reverse=True)
        if goal_clips:
            highlight_clips.append(goal_clips[0][0])
            total_duration += clip_duration

        # Add clips to fill the highlight duration
        while total_duration < max_duration:
            for label in sorted_labels:
                # Skip if we've reached max duration
                if total_duration >= max_duration:
                    break

                # Add clips with highest confidence first
                if label in labeled_clips and labeled_clips[label]:
                    # Sort clips by confidence and select the highest
                    sorted_clips = sorted(labeled_clips[label], key=lambda x: x[1], reverse=True)
                    highlight_clips.append(sorted_clips[0][0])
                    labeled_clips[label].remove(sorted_clips[0])
                    total_duration += clip_duration

        # Video writing process
        output_path = f'highlights_{highlight_duration_minutes}min.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Create video writer
        out = cv2.VideoWriter(output_path, fourcc, fps,
                               (highlight_clips[0][0].shape[1], highlight_clips[0][0].shape[0]))

        # Stitch clips together by writing frames
        for clip in highlight_clips:
            for frame in clip:
                out.write(frame)

        out.release()

        return output_path

def main():
    # Get video path from user
    video_path = 'Test_video_LowRes_Small.mp4'

    # Validate video path
    if not os.path.exists(video_path):
        print("Invalid video path. Please check and try again.")
        return

    # Ask for highlight duration
    while True:
        try:
            duration = int(input("How many minutes of highlights do you want? (3/5): "))
            if duration in [3, 5]:
                break
            else:
                print("Please choose 3 or 5 minutes.")
        except ValueError:
            print("Please enter a valid number.")

    # Generate highlights
    generator = HighlightGenerator()
    output_video = generator.create_highlights(video_path, duration)

    print(f"Highlights generated successfully: {output_video}")

if __name__ == "__main__":
    main()