# Kafka Video Processing Pipeline

- Created By : Rupesh Chaudhari [AI Engineer]

## Overview
This repository contains a Kafka-based video processing pipeline that consumes video frames, processes them using YOLO-based models, and overlays metadata using Flask for visualization.

## Prerequisites
- Install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/).
- Ensure `Kafka` and `MongoDB` are properly set up.

## Usage
### Find Your Test Data and Weight Files
Find test data and weight files from the following link:
[Model Weights & Video Data](https://automatonai1-my.sharepoint.com/:f:/g/personal/rupesh_chaudhari_automatonai_com/ErDF9tKPs9RGi7Eyjya-zqsBvOSxdL72hUwyB9BCsJf_xQ?e=HAI6NR)

### A. Running the Pipeline Locally
#### 1. Clone the Repository
```bash
  git clone "<REPOSITORY_NAME>"
```
#### 2. Navigate to the Project Directory
```bash
  cd <project_directory>
```
#### 3. Start Docker Services
```bash
docker-compose up -d
```
#### 4. Run the Producer
```bash
python producer.py
```
#### 5. Run the Consumer
```bash
python consum.py
```
#### 6. Run the Flask Server
```bash
python overlay_flask.py
```

## B. Customization
### Changing Video Paths
- Update the `video_list.txt` file inside the project directory to specify new video sources.

### Modifying Model and Weights
- Update `model_list.txt` to include new models.

### Modifying Business Logic
- Edit `business_logic.py` to modify processing logic for:
  - Ticket Line Exceed Detection
  - Intrusion Detection
  - Edge-Crossing Detection
- Ensure correct video file paths in `business_logic.py`.

### Kafka Topics
- Modify `producer.py` and `consum.py` to change Kafka topic names if needed.

### Flask Template Customization
- Inside the `Template` folder, modify HTML files to change the visualization.
- Edit `overlay_flask.py` if additional metadata or UI modifications are required.



