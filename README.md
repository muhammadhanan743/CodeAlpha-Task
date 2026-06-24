# CodeAlpha AI Internship — Tasks 1, 2 & 4

> **Intern:** [Your Name]  
> **Domain:** Artificial Intelligence  
> **Tasks Completed:** Task 1 · Task 2 · Task 4

---

## 📁 Repository Structure

```
CodeAlpha_AI_Internship/
├── task1_translation/
│   └── translation_tool.py        ← Task 1: Language Translation Tool
├── task2_chatbot/
│   └── faq_chatbot.py             ← Task 2: FAQ Chatbot (NLP)
├── task4_detection/
│   └── object_detection_tracking.py ← Task 4: Object Detection & Tracking
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/YourUsername/CodeAlpha_AI_Internship.git
cd CodeAlpha_AI_Internship

# Install all dependencies
pip install -r requirements.txt
```

---

## ✅ Task 1 — Language Translation Tool

### What it does
- Beautiful dark-themed GUI built with **Tkinter**
- Supports **100+ languages** via the **Google Translate API** (free, no key needed)
- **Swap** source/target languages with one click
- **Copy to clipboard** button for translated text
- **Text-to-Speech** (read output aloud)
- Non-blocking translation using background threads

### Run
```bash
cd task1_translation
python translation_tool.py
```

### How to use
1. Type text in the left panel
2. Select **From** and **To** languages using the dropdowns
3. Click **Translate** (or press `Ctrl+Enter`)
4. Use **🔊 Speak** to hear the translation or **📋 Copy** to copy it

### Libraries Used
| Library | Purpose |
|---|---|
| `tkinter` | GUI framework (built-in Python) |
| `deep-translator` | Free Google Translate wrapper |
| `pyttsx3` | Text-to-speech engine |
| `pyperclip` | Clipboard access |
| `threading` | Non-blocking API calls |

---

## ✅ Task 2 — Chatbot for FAQs

### What it does
- NLP-powered chatbot with **25 AI/ML/Internship FAQs**
- Text preprocessing: **tokenization, lemmatization, stopword removal** (NLTK)
- Intent matching using **TF-IDF vectorization + cosine similarity** (scikit-learn)
- **Bigram** TF-IDF for better phrase matching
- Confidence score shown for every response
- Coloured terminal UI with timestamps
- Graceful fallback when confidence is too low

### Run
```bash
cd task2_chatbot
python faq_chatbot.py
```

### Sample Questions to Try
```
What is machine learning?
How does a neural network work?
What is YOLO?
How many tasks must I complete?
What perks does CodeAlpha offer?
What is the difference between AI, ML, and DL?
```

### How It Works
```
User Input
   ↓ Lowercase + Remove punctuation
   ↓ Tokenize (NLTK)
   ↓ Remove stopwords
   ↓ Lemmatize (WordNetLemmatizer)
   ↓ TF-IDF Vectorization (unigrams + bigrams)
   ↓ Cosine Similarity vs. all FAQ questions
   ↓ Return best match if score > 0.15 threshold
```

### Libraries Used
| Library | Purpose |
|---|---|
| `nltk` | Tokenization, stopwords, lemmatization |
| `scikit-learn` | TF-IDF + cosine similarity |
| `colorama` | Coloured terminal output |

---

## ✅ Task 4 — Object Detection & Tracking

### What it does
- Real-time detection using **YOLOv8n** (nano — fast and lightweight)
- **ByteTrack** multi-object tracking (built into ultralytics)
- Unique colour-coded **bounding boxes** per object class
- **Motion trails** showing each tracked object's path
- **HUD overlay** with FPS, frame count, and active track count
- Screenshot with `S` key; quit with `Q`
- Supports **webcam, video files, and images**
- Optional `--save` flag to export tracked video

### Run
```bash
cd task4_detection

# Webcam (default)
python object_detection_tracking.py

# Video file
python object_detection_tracking.py --source path/to/video.mp4

# Single image
python object_detection_tracking.py --source path/to/image.jpg

# Save output video
python object_detection_tracking.py --source video.mp4 --save
```

> **Note:** YOLOv8n weights (`yolov8n.pt`, ~6 MB) are downloaded automatically on first run.

### Keyboard Controls
| Key | Action |
|---|---|
| `Q` | Quit |
| `S` | Save screenshot |

### Libraries Used
| Library | Purpose |
|---|---|
| `ultralytics` | YOLOv8 model + ByteTrack tracking |
| `opencv-python` | Video capture, frame rendering |

---

## 🔬 Technical Highlights

| Task | Key AI Technique |
|---|---|
| Translation | REST API integration + threading |
| Chatbot | TF-IDF + Cosine Similarity + NLP pipeline |
| Detection | CNN-based object detection + multi-object tracking |

---

## 📤 Submission Checklist

- [x] Source code uploaded to GitHub (`CodeAlpha_AI_Internship`)
- [x] LinkedIn post with video explanation + GitHub link
- [x] Submission form completed (via WhatsApp group link)
- [x] Minimum 2 tasks completed ✓ (3 tasks submitted)

---

*Made with ❤️ for the CodeAlpha AI Internship Program*

Contribution: 2025-06-16 20:00
