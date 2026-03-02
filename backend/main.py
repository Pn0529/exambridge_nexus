from backend.routes.auth import router as auth_router
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.nlp_service import extract_text_from_pdf, analyze_text_against_syllabus
from backend.services.youtube_service import fetch_youtube_videos
from backend.utils.syllabus_loader import load_syllabus
import os
import uvicorn

app = FastAPI(title="ExamBridge Nexus Backend")

# -------------------------------
# ✅ CORS CONFIG (IMPORTANT)
# -------------------------------
origins = [
    "https://pothulaannapurna8.github.io",
    "http://localhost:3000",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# ROUTERS
# -------------------------------
app.include_router(auth_router)

# -------------------------------
# CACHE STORAGE
# -------------------------------
analysis_cache = {}

# -------------------------------
# ROOT
# -------------------------------
@app.get("/")
def home():
    return {
        "message": "ExamBridge Nexus Backend Running 🚀",
        "status": "healthy"
    }

# -------------------------------
# ANALYZE PDF
# -------------------------------
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

    # Save in cache
    analysis_cache[branch] = results

    return {
        "success": True,
        "branch": branch,
        "analysis": results
    }

# -------------------------------
# PRIORITY TOPICS
# -------------------------------
@app.get("/priority/{branch}")
def get_priority(branch: str, top_n: int = 5):
    branch = branch.lower()

    if branch not in analysis_cache:
        raise HTTPException(status_code=404, detail="No analysis found for this branch")

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
        "success": True,
        "branch": branch,
        "priority_topics": enriched_topics
    }

# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)