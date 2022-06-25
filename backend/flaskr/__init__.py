from hashlib import new
import json
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={"/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()

        try:
            return jsonify(
                {
                    "success": True,
                    "categories": {
                        category.id: category.type for category in categories
                    },
                    "total_categories": len(categories),
                }
            )

        except:
            abort(404)

    @app.route("/questions")
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        current_questions = paginate_questions(request, selection=questions)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(questions),
                "categories": {
                    category.id: category.type for category in categories},
                "current_category": categories[0].type,
                "success": True,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_questions(question_id):
        question_to_delete = Question.query.filter(
            Question.id == question_id
        ).one_or_none()
        questions = Question.query.order_by(Question.id).all()
        try:
            if question_to_delete is None:
                abort(404)

            question_to_delete.delete()
            current_question = paginate_questions(request, selection=questions)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_question,
                    "total_questions": len(questions),
                },
            )
        except:
            abort(404)

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", "")
        new_answer = body.get("answer", "")
        new_category = body.get("category", 1)
        new_difficulty = body.get("difficulty", 1)
        search_term = body.get("searchTerm", "")

        if (new_question == "" or new_answer == "") and search_term == "":
            abort(422)

        try:
            if search_term:
                search_result = Question.query.filter(
                    Question.question.ilike(f"%{search_term}%")
                ).all()
                current_result = paginate_questions(
                    request, selection=search_result)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_result,
                        "total_questions": len(search_result),
                    }
                )
            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty,
                )
                question.insert()

                questions = question.query.order_by(
                    Question.id
                    ).all()
                current_questions = paginate_questions(
                    request, selection=questions)

                return (
                    jsonify(
                        {
                            "success": True,
                            "created": question.id,
                            "questions": current_questions,
                            "total_questions": len(questions),
                        }
                    ),
                    201,
                )
        except:
            abort(422)

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        try:
            category = Category.query.filter(
                Category.id == category_id).one_or_none()

            if category is None:
                abort(404)

            questions = (
                Question.query.order_by(Question.id)
                .filter(Question.category == category_id)
                .all()
            )
            current_question = paginate_questions(request, selection=questions)

            return jsonify(
                {
                    "success": True,
                    "questions": current_question,
                    "total_questions": len(questions),
                    "current_category": category.type,
                }
            )
        except:
            abort(404)

    @app.route("/categories/<int:category_id>/questions")
    def retrieve_questions_by_category(category_id):
        try:
            questions_by_category = Question.query.filter(
                Question.category == category_id
            ).all()

            current_questions = paginate_questions(
                request, selection=questions_by_category
            )
            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(questions_by_category),
                    "current_category": category_id,
                }
            )
        except:
            abort(404)

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        try:
            body = request.get_json()

            category = body.get("quiz_category")
            previous_questions = body.get("previous_questions")

            if (category is None) or (previous_questions is None):
                abort(400)

            if category["type"] == "click":
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(
                    category=category["id"]
                    ).all()
            # generate random questions
            random_questions = (
                questions[random.randrange(0, len(questions))].format()
                if len(questions) > 0
                else None
            )

            return jsonify({"success": True, "question": random_questions})
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "Resource Not Found"}),
            404,)

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
                }),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                "success": False,
                "error": 400,
                "message": "bad request"
                }),
            400,
        )

    @app.errorhandler(500)
    def bad_request(error):
        return (
            jsonify({
                "success": False,
                "error": 500,
                "message": "Internal server error"
                }),
            500,
        )

    return app
