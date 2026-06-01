"""Recommendations powered by resume intelligence and static datasets."""

from app.services import recommendation_service as svc

recommend_learning_plan = svc.recommend_learning_plan
recommend_internships = svc.recommend_internships
build_career_roadmap = svc.build_career_roadmap
build_dashboard_recommendations = svc.build_dashboard_recommendations
