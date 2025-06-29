# 🎯 YouTube Viral Shorts Automation System

An AI-powered automation system that discovers viral YouTube Shorts, analyzes their patterns, generates creative new Shorts using AI, and uploads them — every 6 hours — with the goal of learning and transitioning into the AI field.

---

## 📌 Project Overview

This system automates the end-to-end pipeline for content generation based on trending YouTube videos:

- ⏰ Scheduled every 6 hours via AWS EventBridge
- 🔎 Finds the top 10 most viral videos (5M+ views in 24hrs)
- 🧠 Extracts common patterns, keywords, tags, and topics
- ✍️ Uses AI to generate new video scripts and visuals
- 🎥 Creates and uploads a new YouTube Short via API

---

## 🧠 Why I Built This

As an Identity & Access Management (IAM) Engineer transitioning into the AI field, I wanted to design a real-world AI system from scratch. This project is a practical learning experience covering:

- Cloud automation using AWS Lambda & EventBridge  
- Real-time data processing via APIs  
- AI content generation using Python + open tools  
- Scalable serverless architecture  
- System design for creative automation

---

## 🧱 Architecture

```text
+--------------------+
|  EventBridge (6h)  |
+--------------------+
          |
          v
+---------------------+
|  Data Collector     | <-- YouTube API or scraping
| (Lambda Function)   |
+---------------------+
          |
          v
+----------------------+
|  Content Analyzer     | <-- Extract title, tags, trends
|  (AI/NLP Module)      |
+----------------------+
          |
          v
+----------------------+
|  Video Generator     | <-- TTS + FFmpeg + Assets
| (Script + Audio/Video)|
+----------------------+
          |
          v
+---------------------+
|  Video Uploader     | <-- YouTube API upload
+---------------------+

| Component      | Tool/Service                 |
| -------------- | ---------------------------- |
| Scheduling     | AWS EventBridge              |
| Automation     | AWS Lambda (Python)          |
| Data Storage   | DynamoDB, S3                 |
| Video Input    | YouTube Data API / Scraper   |
| Analysis       | Python, spaCy / NLTK         |
| Video Creation | FFmpeg, AI TTS, Public Media |
| Upload         | YouTube Data API v3          |

🚀 Features Implemented
✅ AWS Lambda trigger every 6 hours (scheduler working)

✅ Config and modular pipeline

✅ YouTube API setup & tested

⏳ Video discovery logic (in progress)

⏳ Content analysis pipeline

⏳ AI-powered script generation

⏳ TTS + video generation with FFmpeg

⏳ Auto-uploading to YouTube channel

📁 File Structure
python
Copy
Edit
youtube-automation/
│
├── lambda/
│   ├── handler.py           # Main Lambda entry point
│   ├── config.py            # Configuration and constants
│   ├── six.py               # Support file (optional)
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
🧪 How to Run (Optional)
Coming soon: Full deployment instructions using AWS SAM / zip deployment
(For now, the Lambda functions can be deployed manually via the AWS Console)


📈 Roadmap
 Set up serverless scheduling and Lambda

 Implement viral video discovery logic

 Analyze trending elements (title, tags, keywords)

 Generate creative script using LLM or prompt template

 Generate media (TTS + visuals)

 Auto-upload to YouTube

 Monitor analytics and add feedback loop

🤝 Contributions & Feedback
This project is part of my learning journey.
If you're an AI engineer, cloud architect, or creative technologist — I welcome feedback, pull requests, or ideas!

📬 Contact
GitHub: @mbommakanti

LinkedIn: Maneesh Bommakanti

