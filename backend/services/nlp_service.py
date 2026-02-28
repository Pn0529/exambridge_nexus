import pdfplumber
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(contents: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
    return text


def calculate_similarity(text1: str, text2: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return float(similarity[0][0])


def analyze_text_against_syllabus(text: str, syllabus_data: dict):
    results = {}

    for subject, topics in syllabus_data.items():
        subject_scores = {}
        
        for topic_name, subtopics in topics.items():
            combined_topic_text = " ".join(subtopics)
            score = calculate_similarity(text, combined_topic_text)
            subject_scores[topic_name] = round(score, 3)

        sorted_scores = dict(
            sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
        )

        results[subject] = sorted_scores

    return results
