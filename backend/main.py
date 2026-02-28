from backend.routes.auth import router as auth_router
from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.services.nlp_service import extract_text_from_pdf, analyze_text_against_syllabus
from backend.services.youtube_service import fetch_youtube_videos
from backend.utils.syllabus_loader import load_syllabus
from backend.utils.database import users_collection

app = FastAPI(title="ExamBridge Nexus Backend")
app.include_router(auth_router)
analysis_cache = {}


@app.get("/")
def home():
    return {"message": "ExamBridge Nexus Backend Running 🚀"}


@app.post("/analyze/{branch}")
async def analyze_pdf(branch: str, file: UploadFile = File(...)):
    branch = branch.lower()

    syllabus_data = load_syllabus(branch)
    if syllabus_data is None:
        raise HTTPException(status_code=400, detail="Branch not supported")

    contents = await file.read()

    text = extract_text_from_pdf(contents)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text")

    results = analyze_text_against_syllabus(text, syllabus_data)

    analysis_cache[branch] = results

    return {
        "branch": branch,
        "analysis": results,
        "status": "success"
    }


@app.get("/priority/{branch}")
def get_priority(branch: str, top_n: int = 5):
    branch = branch.lower()

    if branch not in analysis_cache:
        raise HTTPException(status_code=404, detail="No analysis found")

    analysis = analysis_cache[branch]

    all_scores = []

    for subject, topics in analysis.items():
        for topic, score in topics.items():
            all_scores.append((subject, topic, score))

    ranked = sorted(all_scores, key=lambda x: x[2], reverse=True)
    top_topics = ranked[:top_n]

    enriched_topics = []

    for subject, topic, score in top_topics:
        videos = fetch_youtube_videos(f"GATE {topic} lecture")

        enriched_topics.append({
            "subject": subject,
            "topic": topic,
            "score": score,
            "videos": videos
        })

    return {
        "branch": branch,
        "priority_topics": enriched_topics
    }