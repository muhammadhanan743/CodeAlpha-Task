"""
CodeAlpha Task 2: Chatbot for FAQs
Uses NLTK + TF-IDF cosine similarity for intent matching.
Install: pip install nltk scikit-learn colorama
"""

import sys
import re
import math
import json
import textwrap
from datetime import datetime

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    # Download required NLTK data silently
    for pkg in ["punkt", "stopwords", "wordnet", "omw-1.4", "punkt_tab"]:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass
    NLTK_OK = True
except ImportError:
    NLTK_OK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False
    class Fore:
        CYAN = GREEN = YELLOW = RED = MAGENTA = BLUE = WHITE = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""
    class Back:
        BLUE = ""

# ── FAQ Database ───────────────────────────────────────────────────────────────
FAQ_DATA = [
    # General AI / CodeAlpha
    {
        "question": "What is artificial intelligence?",
        "answer": "Artificial Intelligence (AI) is the simulation of human intelligence by machines. It enables computers to learn, reason, perceive, and make decisions — powering applications like speech recognition, image classification, recommendation systems, and autonomous vehicles."
    },
    {
        "question": "What is machine learning?",
        "answer": "Machine Learning (ML) is a subset of AI where algorithms learn patterns from data without being explicitly programmed. Models improve automatically with experience. Key types include supervised learning, unsupervised learning, and reinforcement learning."
    },
    {
        "question": "What is deep learning?",
        "answer": "Deep Learning is a subset of ML that uses neural networks with many layers (hence 'deep') to learn complex representations from raw data. It powers image recognition, natural language processing, and generative AI."
    },
    {
        "question": "What is a neural network?",
        "answer": "A neural network is a computational model inspired by the human brain. It consists of layers of interconnected nodes (neurons) that process input data, learn weights through training, and produce predictions or classifications."
    },
    {
        "question": "What is NLP?",
        "answer": "Natural Language Processing (NLP) is the field of AI that enables machines to understand, interpret, and generate human language. It powers chatbots, translation tools, sentiment analysis, and text summarization."
    },
    {
        "question": "What is computer vision?",
        "answer": "Computer Vision is a field of AI that trains computers to interpret visual information from images and videos — enabling object detection, face recognition, medical imaging, and self-driving cars."
    },
    {
        "question": "What is a large language model?",
        "answer": "A Large Language Model (LLM) is a type of AI trained on massive text datasets to understand and generate human-like text. Examples include GPT-4, Claude, Gemini, and LLaMA."
    },
    {
        "question": "What is transfer learning?",
        "answer": "Transfer learning is a technique where a model trained on one task is fine-tuned for a different but related task. It saves time and data by leveraging pre-existing knowledge — for example, using a model trained on ImageNet for medical image diagnosis."
    },
    {
        "question": "What is overfitting in machine learning?",
        "answer": "Overfitting occurs when a model learns the training data too well — including its noise — and performs poorly on unseen data. Solutions include regularization, dropout, cross-validation, and using more training data."
    },
    {
        "question": "What is a convolutional neural network?",
        "answer": "A Convolutional Neural Network (CNN) is a deep learning architecture designed for processing grid-structured data like images. It uses convolutional layers to automatically detect spatial features like edges, textures, and shapes."
    },
    {
        "question": "What is LSTM?",
        "answer": "Long Short-Term Memory (LSTM) is a type of recurrent neural network (RNN) capable of learning long-term dependencies in sequential data. It is widely used in time-series forecasting, speech recognition, and text generation."
    },
    {
        "question": "What is reinforcement learning?",
        "answer": "Reinforcement Learning (RL) is a type of machine learning where an agent learns to make decisions by interacting with an environment and receiving rewards or penalties. It powers game-playing AIs like AlphaGo and robotics control."
    },
    # CodeAlpha Internship
    {
        "question": "What is CodeAlpha?",
        "answer": "CodeAlpha is a leading software development company dedicated to driving innovation across emerging technologies. It offers internship programs in AI, web development, and more, giving students hands-on industry experience."
    },
    {
        "question": "How many tasks must I complete for the internship?",
        "answer": "You must complete a minimum of 2 or 3 tasks out of the 4 assigned in your domain. Submitting only 1 task is considered incomplete and a certificate will not be issued."
    },
    {
        "question": "What perks does the CodeAlpha internship offer?",
        "answer": "Interns receive an Offer Letter, a QR-verified Completion Certificate, a Unique ID Certificate, a Letter of Recommendation (based on performance), job placement support, and resume building assistance."
    },
    {
        "question": "How do I submit my CodeAlpha tasks?",
        "answer": "Upload your source code to GitHub in a repository named 'CodeAlpha_ProjectName', post a video explanation on LinkedIn with the GitHub link, and submit the completed form shared in your WhatsApp group."
    },
    {
        "question": "What is YOLO?",
        "answer": "YOLO (You Only Look Once) is a real-time object detection algorithm that processes images in a single forward pass through a CNN, making it extremely fast and suitable for video-based detection tasks."
    },
    {
        "question": "What is object detection?",
        "answer": "Object detection is a computer vision task that identifies and localizes objects in an image or video by drawing bounding boxes around them and labeling each with a class name and confidence score."
    },
    {
        "question": "What is cosine similarity?",
        "answer": "Cosine similarity measures the angle between two vectors in a high-dimensional space. A score of 1.0 means they are identical in direction (very similar), while 0 means they are orthogonal (completely different). It is widely used in NLP to compare text."
    },
    {
        "question": "What is TF-IDF?",
        "answer": "TF-IDF (Term Frequency-Inverse Document Frequency) is a numerical statistic that reflects how important a word is to a document in a corpus. It is used in information retrieval and text mining to weigh terms by relevance."
    },
    {
        "question": "What programming languages are used in AI?",
        "answer": "Python is the dominant language in AI and ML due to its rich ecosystem (TensorFlow, PyTorch, scikit-learn, NLTK). R is used for statistical analysis, and Julia for high-performance numerical computing. C++ is used in performance-critical deployments."
    },
    {
        "question": "What is OpenCV?",
        "answer": "OpenCV (Open Source Computer Vision Library) is an open-source library for real-time image and video processing. It supports operations like edge detection, object tracking, face recognition, and camera capture in Python, C++, and Java."
    },
    {
        "question": "How does a chatbot work?",
        "answer": "A chatbot processes user input text, extracts intent using NLP techniques (keyword matching, TF-IDF, embeddings, or LLMs), retrieves or generates the most appropriate response, and returns it to the user. Rule-based chatbots use predefined responses; AI chatbots learn from data."
    },
    {
        "question": "What is the difference between AI, ML, and DL?",
        "answer": "AI is the broad field of making machines intelligent. Machine Learning (ML) is a subset that learns from data. Deep Learning (DL) is a subset of ML using multi-layer neural networks. Think of it as: AI ⊃ ML ⊃ DL."
    },
    {
        "question": "What is a GAN?",
        "answer": "A Generative Adversarial Network (GAN) consists of two neural networks — a Generator that creates fake data and a Discriminator that tries to distinguish fake from real. They compete until the generator produces convincingly realistic outputs, used in image synthesis, music generation, and more."
    },
]


# ── NLP Pipeline ───────────────────────────────────────────────────────────────
class FAQChatbot:
    CONFIDENCE_THRESHOLD = 0.15

    def __init__(self):
        self.faqs = FAQ_DATA
        self.questions = [faq["question"] for faq in self.faqs]
        self.answers   = [faq["answer"]   for faq in self.faqs]

        if NLTK_OK:
            self.lemmatizer = WordNetLemmatizer()
            try:
                self.stop_words = set(stopwords.words("english"))
            except Exception:
                self.stop_words = set()
        else:
            self.lemmatizer = None
            self.stop_words = set()

        # Build TF-IDF index
        if SKLEARN_OK:
            processed = [self._preprocess(q) for q in self.questions]
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(processed)
        else:
            self.vectorizer = None

    def _preprocess(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = text.split()
        if NLTK_OK and self.lemmatizer:
            tokens = [self.lemmatizer.lemmatize(t) for t in tokens
                      if t not in self.stop_words and len(t) > 1]
        return " ".join(tokens)

    def get_response(self, user_input: str):
        """Return (answer, matched_question, confidence)."""
        if not user_input.strip():
            return "Please type a question!", "", 0.0

        if not SKLEARN_OK:
            # Fallback: simple keyword matching
            best_score, best_idx = 0, 0
            inp = user_input.lower()
            for i, q in enumerate(self.questions):
                words = set(q.lower().split())
                score = sum(1 for w in inp.split() if w in words) / max(len(words), 1)
                if score > best_score:
                    best_score, best_idx = score, i
            if best_score > 0.1:
                return self.answers[best_idx], self.questions[best_idx], best_score
            return ("I'm not sure about that. Try rephrasing or ask something about "
                    "AI, machine learning, or the CodeAlpha internship."), "", 0.0

        processed_input = self._preprocess(user_input)
        vec = self.vectorizer.transform([processed_input])
        scores = cosine_similarity(vec, self.tfidf_matrix).flatten()
        best_idx = int(scores.argmax())
        confidence = float(scores[best_idx])

        if confidence < self.CONFIDENCE_THRESHOLD:
            return (
                "I don't have a confident answer for that. "
                "Try asking about AI, ML, deep learning, NLP, YOLO, or the CodeAlpha internship.",
                "", confidence
            )
        return self.answers[best_idx], self.questions[best_idx], confidence


# ── CLI Chat Interface ─────────────────────────────────────────────────────────
def wrap(text, width=72, indent="   "):
    return "\n".join(indent + line
                     for line in textwrap.fill(text, width).split("\n"))


def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
  ╔══════════════════════════════════════════════════════════╗
  ║          CodeAlpha AI Internship — Task 2               ║
  ║              FAQ Chatbot  (NLP + TF-IDF)                ║
  ╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
  {Fore.WHITE}Ask me about AI, Machine Learning, Deep Learning,
  NLP, computer vision, or the CodeAlpha internship!

  {Fore.YELLOW}Commands:{Style.RESET_ALL}  'list' — show all FAQs   |   'quit' — exit
"""
    print(banner)


def print_bot(text: str, matched: str = "", confidence: float = 0.0):
    now = datetime.now().strftime("%H:%M")
    print(f"\n  {Fore.CYAN}🤖 Bot{Style.DIM} [{now}]{Style.RESET_ALL}")
    if matched:
        print(f"  {Fore.MAGENTA}Matched: \"{matched}\" "
              f"({Fore.GREEN}{confidence*100:.0f}%{Fore.MAGENTA} confidence){Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}{wrap(text)}{Style.RESET_ALL}\n")
    print(f"  {Fore.CYAN}{'─'*60}{Style.RESET_ALL}")


def print_user(text: str):
    now = datetime.now().strftime("%H:%M")
    print(f"\n  {Fore.GREEN}You{Style.DIM} [{now}]{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}{text}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}{'─'*60}{Style.RESET_ALL}")


def main():
    print_banner()
    bot = FAQChatbot()

    libs = []
    if NLTK_OK:    libs.append("NLTK ✓")
    else:          libs.append(f"{Fore.YELLOW}NLTK ✗ (pip install nltk){Style.RESET_ALL}")
    if SKLEARN_OK: libs.append("scikit-learn ✓")
    else:          libs.append(f"{Fore.YELLOW}scikit-learn ✗ (pip install scikit-learn){Style.RESET_ALL}")

    print(f"  Libraries: {' | '.join(libs)}")
    print(f"  Loaded {len(FAQ_DATA)} FAQs into TF-IDF index.\n")

    while True:
        try:
            user_input = input(f"  {Fore.GREEN}You ▶ {Style.RESET_ALL}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print(f"\n  {Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
            break

        if user_input.lower() == "list":
            print(f"\n  {Fore.CYAN}Available FAQs:{Style.RESET_ALL}")
            for i, q in enumerate(FAQ_DATA, 1):
                print(f"  {Fore.YELLOW}{i:2}.{Style.RESET_ALL} {q['question']}")
            print()
            continue

        print_user(user_input)
        answer, matched, conf = bot.get_response(user_input)
        print_bot(answer, matched, conf)


if __name__ == "__main__":
    main()
