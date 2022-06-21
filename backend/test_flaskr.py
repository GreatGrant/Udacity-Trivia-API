import os
import re
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.new_question = {
            "question": "this is a sample question",
            "answer": "This is a sample answer",
            "difficulty": 1,
            "category": 1,
        }
        self.search_term = {"searchTerm": "invented peanut butter"}
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "postgres", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # def test_get_questions(self):
    #     response = self.client().get("/questions")
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["questions"])
    #     self.assertTrue(data["total_questions"])
    #     self.assertTrue(data["questions"])
    #     self.assertTrue(len(data["questions"]), 10)

    # def test_404_sent_requesting_beyond_valid_page(self):
    #     response = self.client().get("questions/10000")
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")

    # def test_get_categories(self):
    #     response = self.client().get("/categories")
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(data["success"])
    #     self.assertTrue(data["categories"])
    #     self.assertEqual(data["total_categories"], 6)

    # def test_delete_question(self):
    #     response = self.client().delete("questions/23")
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertEqual(data["deleted"], 23)
    #     self.assertTrue(data["questions"])
    #     self.assertTrue(data["total_questions"])

    # def test_create_question(self):
    #     response = self.client().post("/questions", json = self.new_question)
    #     data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["total_questions"])
    #     self.assertTrue(len(data["questions"]))

    def test_search_question(self):
        response = self.client().post("/questions/search", json=self.search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 1)

    def test_retrieve_questions_by_category(self):
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertNotEqual(len(data["questions"]), 0)
        self.assertEqual(data["current_category"], 1)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
