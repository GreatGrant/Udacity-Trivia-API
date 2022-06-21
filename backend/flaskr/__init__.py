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
    CORS

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

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

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        paginated_questions = paginate_questions(request, selection=questions)

        return jsonify(
            {
                "success": True,
                "questions": paginated_questions,
                "total_questions": len(questions),
                "categories": {category.id: category.type for category in categories},
                "current_category": categories[0].type,
                "success": True,
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

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
            paginated_questions = paginate_questions(request, selection=questions)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": paginated_questions,
                    "total_questions": len(questions),
                },
            )
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", "")
        new_answer = body.get("answer", "")
        new_category = body.get("category", 1)
        new_difficulty = body.get("difficulty", 1)

        if new_question == "" or new_answer == "":
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )

            question.insert()

            questions = question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, selection=questions)

            return (
                jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": paginated_questions,
                        "total_questions": len(questions),
                    }
                ),
                201,
            )
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=['POST'])
    def search_question():
        search_term = request.get_json().get("searchTerm", "")

        if search_term == "":
            abort(404)
        
        search_result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        if len(search_result) == 0:
            abort(404)

        paginated_result = paginate_questions(request, selection=search_result)

        return jsonify({
                "success": True,
                "questions": paginated_result,
                "total_questions": len(search_result),
            }), 200
        abort(404)



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource Not Found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(500)
    def bad_request(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal server error"}
            ),
            500,
        )

    return app
