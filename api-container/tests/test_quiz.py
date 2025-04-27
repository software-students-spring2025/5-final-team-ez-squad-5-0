import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from app.routes.quiz import quiz_bp


class TestQuizModule(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["JWT_SECRET_KEY"] = "test-key"
        self.app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
        self.jwt = JWTManager(self.app)
        self.client = self.app.test_client()

        with self.app.app_context():
            self.token = create_access_token(identity=str(ObjectId()))

        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

        self.jwt_patcher = patch("app.routes.quiz.jwt_required")
        self.mock_jwt_required = self.jwt_patcher.start()
        self.mock_jwt_required.return_value = lambda f: f

        self.identity_patcher = patch("app.routes.quiz.get_jwt_identity")
        self.mock_get_jwt_identity = self.identity_patcher.start()
        self.mock_get_jwt_identity.return_value = str(ObjectId())

        self.mongo_patcher = patch("app.routes.quiz.mongo")
        self.mock_mongo = self.mongo_patcher.start()

        self.mock_users = MagicMock()
        self.mock_quiz_batches = MagicMock()
        self.mock_quiz_scores = MagicMock()
        self.mock_quiz_responses = MagicMock()
        self.mock_mongo.db.users = self.mock_users
        self.mock_mongo.db.quiz_batches = self.mock_quiz_batches
        self.mock_mongo.db.quiz_scores = self.mock_quiz_scores
        self.mock_mongo.db.quiz_responses = self.mock_quiz_responses

    def tearDown(self):
        self.jwt_patcher.stop()
        self.identity_patcher.stop()
        self.mongo_patcher.stop()

    def test_get_score_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.get("/api/quiz/score", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_get_status_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.get("/api/quiz/status", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_get_batch_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.get("/api/quiz/batch", headers=self.auth_headers)
        self.assertEqual(response.status_code, 400)

    def test_get_question_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.get("/api/quiz/question", headers=self.auth_headers)
        self.assertEqual(response.status_code, 400)

    def test_submit_answer_missing_params(self):
        response = self.client.post(
            "/api/quiz/answer", headers=self.auth_headers, json={}
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_answer_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.post(
            "/api/quiz/answer",
            headers=self.auth_headers,
            json={"question_id": 1, "answer": "A"},
        )
        self.assertEqual(response.status_code, 400)

    def test_check_partner_response_missing_params(self):
        response = self.client.get(
            "/api/quiz/check-partner-response", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

    def test_check_partner_response_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.get(
            "/api/quiz/check-partner-response?question_id=1", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

    def test_get_batch_results_no_partner(self):
        self.mock_users.find_one.return_value = {"_id": ObjectId()}
        response = self.client.get(
            "/api/quiz/batch/123/results", headers=self.auth_headers
        )
        self.assertEqual(response.status_code, 400)

    def test_get_score_with_matches(self):
        self.mock_users.find_one.return_value = {
            "_id": ObjectId(),
            "partner_id": str(ObjectId()),
        }
        self.mock_quiz_responses.find.return_value = []
        self.mock_quiz_scores.find_one.return_value = {"score": 100}
        self.mock_quiz_responses.count_documents.return_value = 2
        response = self.client.get("/api/quiz/score", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_get_score_with_partner_no_matches(self):
        self.mock_users.find_one.return_value = {
            "_id": ObjectId(),
            "partner_id": str(ObjectId()),
        }
        self.mock_quiz_responses.find.return_value = []
        self.mock_quiz_scores.find_one.return_value = {"score": 0}
        self.mock_quiz_responses.count_documents.return_value = 0
        response = self.client.get("/api/quiz/score", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_get_status_with_partner(self):
        self.mock_users.find_one.return_value = {
            "_id": ObjectId(),
            "partner_id": str(ObjectId()),
        }
        self.mock_quiz_batches.find_one.return_value = None
        self.mock_quiz_responses.distinct.side_effect = [[], []]
        self.mock_quiz_scores.find_one.return_value = {"score": 10}
        response = self.client.get("/api/quiz/status", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
