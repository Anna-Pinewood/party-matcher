from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # показывает лучшее качество


def list_similarity(list1, list2):
    if not list1 or not list2:
        return 0
    set1, set2 = set(list1), set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


def text_similarity(text1, text2):
    if not text1 or not text2:
        return 0
    embeddings = model.encode([text1, text2])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]


def calculate_similarity(person1: dict, person2: dict) -> float:
    score = 0
    weight = {
        "gender": 1,
        "age": 1,
        "country": 1,
        "city": 1,
        "professional_field": 2,
        "professional_interests": 3,
        "languages": 2,
        "study_universities": 2,
        "professional_experience": 4,
        "skills": 3,
        "projects": 2,
        "achievements": 2,
    }

    score += weight["gender"] * (1 if person1["gender"] == person2["gender"] else 0)
    score += weight["country"] * (1 if person1["country"] == person2["country"] else 0)
    score += weight["city"] * (1 if person1["city"] == person2["city"] else 0)
    score += weight["professional_field"] * (1 if person1["professional_field"] == person2["professional_field"] else 0)

    age_diff = abs(person1["age"] - person2["age"])
    score += weight["age"] * (1 - min(age_diff / 100, 1))

    score += weight["professional_interests"] * list_similarity(person1["professional_interests"],
                                                                person2["professional_interests"])
    score += weight["languages"] * list_similarity(person1["languages"], person2["languages"])
    score += weight["study_universities"] * list_similarity(person1["study_universities"],
                                                            person2["study_universities"])
    score += weight["skills"] * list_similarity(person1["skills"], person2["skills"])

    exp1 = " ".join([exp["summary"] for exp in person1["professional_experience"]])
    exp2 = " ".join([exp["summary"] for exp in person2["professional_experience"]])
    score += weight["professional_experience"] * text_similarity(exp1, exp2)

    proj1 = " ".join([proj["description"] for proj in person1.get("projects", [])])
    proj2 = " ".join([proj["description"] for proj in person2.get("projects", [])])
    score += weight["projects"] * text_similarity(proj1, proj2)

    ach1 = " ".join(person1.get("achievements", []))
    ach2 = " ".join(person2.get("achievements", []))
    score += weight["achievements"] * text_similarity(ach1, ach2)

    max_score = sum(weight.values())
    return score / max_score
