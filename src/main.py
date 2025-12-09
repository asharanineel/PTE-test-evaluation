# #--- START OF FILE main.py ---

# # This version combines the superior structure of the new code with the
# # critical business logic (test structure validation) from the old code.

# import sys
# import os
# import logging

# # [FIX] Add the project's source directory to the Python path.
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # =============================
# # Setup Central Logger
# # =============================
# # Configure logging to write all terminal output to evaluation.log
# logging.basicConfig(
#     filename="evaluation.log",
#     filemode="a", # 'a' for append
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
#     force=True  # This overrides any default handlers to ensure all logs are captured
# )

# # Create a logger instance for this module
# logger = logging.getLogger(__name__)

# # [NEW] Redirect stdout and stderr to the logger to capture everything
# class StreamToLogger:
#     """
#     Fake file-like stream object that redirects writes to a logger instance.
#     """
#     def __init__(self, logger, level):
#         self.logger = logger
#         self.level = level
#         self.linebuf = ''

#     def write(self, buf):
#         for line in buf.rstrip().splitlines():
#             self.logger.log(self.level, line.rstrip())

#     def flush(self):
#         pass

# sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
# sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)

# logger.info("=========================================================")
# logger.info("           Application starting up...                    ")
# logger.info("=========================================================")


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from pydantic import BaseModel, ValidationError
# from typing import List, Dict, Any
# from datetime import datetime
# from collections import defaultdict
# import pymongo
# from config import settings

# # Import evaluators
# from evaluators.describe_image_evaluator import DescribeImageEvaluator
# from evaluators.read_aloud_evaluator import ReadAloudEvaluator
# from evaluators.retell_lecture_evaluator import RetellLectureEvaluator
# from evaluators.answer_short_question_evaluator import AnswerShortQuestionEvaluator
# from evaluators.repeat_sentence_evaluator import RepeatSentenceEvaluator
# from evaluators.write_email_evaluator import WriteEmailEvaluator
# from evaluators.write_essay_evaluator import WriteEssayEvaluator
# from evaluators.summarize_written_text_evaluator import SummarizeWrittenTextEvaluator
# from evaluators.respond_to_a_situation_evaluator import RespondToASituationEvaluator

# # =============================
# # Initialize App & DB
# # =============================
# app = Flask(__name__)
# CORS(app)

# mongo_client = pymongo.MongoClient(settings.MONGO_URI)
# db = mongo_client["pte_speaking_writing_database"]
# collection = db["speaking_writing"]

# # =============================
# # Mappings and Constants
# # (The rest of the file is unchanged)
# # =============================
# EVALUATOR_MAP = {
#     "describe_image": DescribeImageEvaluator, "read_aloud": ReadAloudEvaluator,
#     "retell_lecture": RetellLectureEvaluator, "answer_short_question": AnswerShortQuestionEvaluator,
#     "repeat_sentence": RepeatSentenceEvaluator, "write_email": WriteEmailEvaluator,
#     "write_essay": WriteEssayEvaluator, "summarize_written_text": SummarizeWrittenTextEvaluator,
#     "respond_to_a_situation": RespondToASituationEvaluator
# }

# PROMPT_TYPE_TO_INPUT_FIELD = {
#     "read_aloud": "paragraph", "repeat_sentence": "sentence", "describe_image": "description",
#     "respond_to_a_situation": "situation", "retell_lecture": "lecture",
#     "answer_short_question": "question", "summarize_written_text": "passage",
#     "write_email": "task", "write_essay": "topic"
# }

# TASK_PATTERN_MAP = {
#     "core": [
#         {"task": "read_aloud", "count": 6}, {"task": "repeat_sentence", "count": 10},
#         {"task": "describe_image", "count": 3}, {"task": "respond_to_a_situation", "count": 3},
#         {"task": "answer_short_question", "count": 6}, {"task": "summarize_written_text", "count": 1},
#         {"task": "write_email", "count": 2}
#     ],
#     "academic": [
#         {"task": "read_aloud", "count": 6}, {"task": "repeat_sentence", "count": 12},
#         {"task": "describe_image", "count": 6}, {"task": "retell_lecture", "count": 4},
#         {"task": "answer_short_question", "count": 12}, {"task": "summarize_written_text", "count": 1},
#         {"task": "write_essay", "count": 1}
#     ]
# }

# CLB_MAPPING = {
#     10: {"speaking": (89, 90), "writing": (90, 90)}, 9: {"speaking": (84, 88), "writing": (88, 89)},
#     8: {"speaking": (76, 83), "writing": (79, 87)}, 7: {"speaking": (68, 75), "writing": (69, 78)},
#     6: {"speaking": (59, 67), "writing": (60, 68)}, 5: {"speaking": (51, 58), "writing": (51, 59)},
#     4: {"speaking": (42, 50), "writing": (41, 50)}, 3: {"speaking": (34, 41), "writing": (32, 40)}
# }

# speaking_tasks = ["read_aloud", "repeat_sentence", "describe_image", "retell_lecture", "answer_short_question", "respond_to_a_situation"]
# writing_tasks = ["summarize_written_text", "write_email", "write_essay"]

# # =============================
# # Pydantic Model
# # =============================
# class EvaluationRequest(BaseModel):
#     exam_type: str
#     user_id: str
#     test_id: str
#     responses: List[Dict[str, Any]]

# # =============================
# # API Endpoints
# # =============================
# @app.route("/evaluate-test-paper", methods=["POST"])
# def evaluate_test_paper():
#     try:
#         req = EvaluationRequest(**request.get_json())
#     except ValidationError as e:
#         logger.error(f"Invalid request format: {e.errors()}")
#         return jsonify({"error": "Invalid request format", "details": e.errors()}), 400

#     if not collection.find_one({"test_id": req.test_id}):
#         logger.error(f"Test paper with test_id {req.test_id} not found")
#         return jsonify({"error": f"Test paper with test_id {req.test_id} not found"}), 404

#     exam_type = req.exam_type.lower()
#     if exam_type not in TASK_PATTERN_MAP:
#         logger.error(f"Invalid exam_type: {exam_type}")
#         return jsonify({"error": f"Invalid exam_type provided: {exam_type}"}), 400

#     expected_tasks = TASK_PATTERN_MAP[exam_type]
#     submitted_q_types = [r.get("question_type") for r in req.responses]
    
#     for task_spec in expected_tasks:
#         task_name = task_spec["task"]
#         expected_count = task_spec["count"]
#         actual_count = submitted_q_types.count(task_name)
#         if actual_count != expected_count:
#             error_msg = f"Task count mismatch for {task_name}: expected {expected_count}, but got {actual_count}"
#             logger.error(error_msg)
#             return jsonify({"error": error_msg}), 400

#     evaluated_responses = defaultdict(list)
#     speaking_scores = []
#     writing_scores = []

#     for response in req.responses:
#         q_type = response.get("question_type")
#         if q_type not in EVALUATOR_MAP:
#             logger.warning(f"Unknown question_type received: {q_type}, skipping.")
#             continue

#         input_field = PROMPT_TYPE_TO_INPUT_FIELD.get(q_type)
#         question = response.get(input_field)
#         user_response = response.get("user_response")

#         if not question or not user_response:
#             logger.error(f"Missing question or user_response for {q_type}")
#             return jsonify({"error": f"Missing data for question_type {q_type}"}), 400

#         evaluator = EVALUATOR_MAP[q_type]()
#         evaluation_result = evaluator.evaluate(question, user_response)
      
#         score = evaluation_result.get("overall_score", 0)
#         if q_type in speaking_tasks:
#             speaking_scores.append(score)
#         elif q_type in writing_tasks:
#             writing_scores.append(score)

#         evaluated_responses[q_type].append({
#             "question": question,
#             "user_response": user_response,
#             "evaluation": evaluation_result
#         })

#     avg_speaking = sum(speaking_scores) / len(speaking_scores) if speaking_scores else 0
#     avg_writing = sum(writing_scores) / len(writing_scores) if writing_scores else 0
  
#     clb_speaking, clb_writing = None, None
#     for level, ranges in CLB_MAPPING.items():
#         if not clb_speaking and ranges["speaking"][0] <= avg_speaking <= ranges["speaking"][1]:
#             clb_speaking = level
#         if not clb_writing and ranges["writing"][0] <= avg_writing <= ranges["writing"][1]:
#             clb_writing = level

#     overall_score_summary = {
#         "average_speaking_score": round(avg_speaking, 2),
#         "average_writing_score": round(avg_writing, 2),
#         "clb_speaking": clb_speaking,
#         "clb_writing": clb_writing,
#         "overall_feedback": f"Evaluation completed for {req.exam_type} mode. {len(req.responses)} responses were processed successfully.",
#         "evaluated_at": datetime.utcnow().isoformat()
#     }

#     update_payload = {
#         "status": "completed",
#         "overall_score": overall_score_summary,
#         **evaluated_responses
#     }

#     try:
#         collection.update_one(
#             {"test_id": req.test_id},
#             {"$set": update_payload}
#         )
#         logger.info(f"Successfully updated evaluation for test_id {req.test_id}")
      
#         updated_document = collection.find_one({"test_id": req.test_id}, {"_id": 0})
#         return jsonify(updated_document)

#     except Exception as e:
#         logger.error(f"Failed to update MongoDB for test_id {req.test_id}: {e}")
#         return jsonify({"error": "Failed to update database", "details": str(e)}), 500

# @app.route("/")
# def home():
#     return jsonify({
#         "message": "Welcome to PTE Evaluator API!",
#         "endpoint": "/evaluate-test-paper"
#     })

# if __name__ == "__main__":
#     logger.info("🚀 Starting Flask PTE Evaluator API on http://localhost:7010")
#     app.run(host="0.0.0.0", port=7010)

#     ################## okkk ########################


# modified on 8/10/2025
# import sys
# import os
# import logging
# import json
# import base64
# from datetime import datetime
# import functools # For wrapping logger

# # Add the project's source directory to the Python path.
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # =============================
# # Setup Central Logger
# # =============================
# # Configure logging to write all terminal output to evaluation.log
# log_file_path = "evaluation.log"

# logging.basicConfig(
#     filename=log_file_path,
#     filemode="a",  # 'a' for append
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO, # Changed to INFO to reduce verbosity by default
#     force=True  # This overrides any default handlers to ensure all logs are captured
# )

# # Create a logger instance for this module
# logger = logging.getLogger(__name__)

# # Redirect stdout and stderr to the logger to capture everything
# class StreamToLogger:
#     """
#     Fake file-like stream object that redirects writes to a logger instance.
#     """
#     def __init__(self, logger_name, level):
#         self.logger = logging.getLogger(logger_name)
#         self.level = level
#         self._write_func = functools.partial(self.logger.log, self.level)

#     def write(self, buf):
#         for line in buf.rstrip().splitlines():
#             if line:
#                 self._write_func(line.rstrip())

#     def flush(self):
#         pass

# sys.stdout = StreamToLogger('STDOUT', logging.INFO)
# sys.stderr = StreamToLogger('STDERR', logging.WARNING)

# logger.info("=========================================================")
# logger.info("           Application starting up...                    ")
# logger.info("=========================================================")

# # Set higher logging levels for noisy external libraries
# logging.getLogger('pymongo.topology').setLevel(logging.WARNING)
# logging.getLogger('pymongo.serverSelection').setLevel(logging.WARNING)
# logging.getLogger('pymongo.connection').setLevel(logging.WARNING)
# logging.getLogger('pymongo.command').setLevel(logging.WARNING)

# logging.getLogger('openai._base_client').setLevel(logging.WARNING)
# logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
# logging.getLogger('httpcore.http11').setLevel(logging.WARNING)
# logging.getLogger('httpx').setLevel(logging.INFO)

# logging.getLogger('numba.core.byteflow').setLevel(logging.ERROR)
# logging.getLogger('numba.core.ssa').setLevel(logging.ERROR)
# logging.getLogger('numba.core.interpreter').setLevel(logging.ERROR)
# logging.getLogger('numba').setLevel(logging.ERROR)

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from pydantic import BaseModel, ValidationError
# from typing import List, Dict, Any, Optional
# from collections import defaultdict
# import pymongo
# from config import settings

# # Import evaluators (ensure these paths are correct for your project structure)
# from evaluators.describe_image_evaluator import DescribeImageEvaluator
# from evaluators.read_aloud_evaluator import ReadAloudEvaluator
# from evaluators.retell_lecture_evaluator import RetellLectureEvaluator
# from evaluators.answer_short_question_evaluator import AnswerShortQuestionEvaluator
# from evaluators.repeat_sentence_evaluator import RepeatSentenceEvaluator
# from evaluators.write_email_evaluator import WriteEmailEvaluator
# from evaluators.write_essay_evaluator import WriteEssayEvaluator
# from evaluators.summarize_written_text_evaluator import SummarizeWrittenTextEvaluator
# from evaluators.respond_to_a_situation_evaluator import RespondToASituationEvaluator
# from evaluators.summarize_group_discussion_evaluator import SummarizeGroupDiscussionEvaluator


# # =============================
# # Initialize App & DB
# # =============================
# app = Flask(__name__)
# CORS(app)

# mongo_client = pymongo.MongoClient(settings.MONGO_URI)
# db = mongo_client["pte_speaking_writing_database"]
# collection = db["speaking_writing"]

# # =============================
# # Mappings and Constants
# # =============================
# EVALUATOR_MAP = {
#     "describe_image": DescribeImageEvaluator,
#     "read_aloud": ReadAloudEvaluator,
#     "retell_lecture": RetellLectureEvaluator,
#     "answer_short_question": AnswerShortQuestionEvaluator,
#     "repeat_sentence": RepeatSentenceEvaluator,
#     "write_email": WriteEmailEvaluator,
#     "write_essay": WriteEssayEvaluator,
#     "summarize_written_text": SummarizeWrittenTextEvaluator,
#     "respond_to_a_situation": RespondToASituationEvaluator,
#     "summarize_group_discussion": SummarizeGroupDiscussionEvaluator
# }

# PROMPT_TYPE_TO_INPUT_FIELD = {
#     "read_aloud": "paragraph", "repeat_sentence": "sentence", "describe_image": "description",
#     "respond_to_a_situation": "situation", "retell_lecture": "lecture",
#     "answer_short_question": "question", "summarize_written_text": "passage",
#     "write_email": "task", "write_essay": "topic",
#     "summarize_group_discussion": "discussion" # Note: 'discussion' here refers to the list of speaker dialogues.
# }

# TASK_PATTERN_MAP = {
#     "core": [
#         {"task": "read_aloud", "count": 6}, {"task": "repeat_sentence", "count": 10},
#         {"task": "describe_image", "count": 3}, {"task": "respond_to_a_situation", "count": 3},
#         {"task": "answer_short_question", "count": 6}, {"task": "summarize_written_text", "count": 1},
#         {"task": "write_email", "count": 2}
#     ],
#     "academic": [
#         {"task": "read_aloud", "count": 1}, {"task": "repeat_sentence", "count": 1},
#         {"task": "describe_image", "count": 1}, {"task": "retell_lecture", "count": 1},
#         {"task": "answer_short_question", "count": 1},{"task": "summarize_group_discussion", "count": 1},
#         {"task": "respond_to_a_situation", "count": 1}, {"task": "summarize_written_text", "count": 1},
#         {"task": "write_essay", "count": 1}
#     ]
# }

# CLB_MAPPING = {
#     10: {"speaking": (89, 90), "writing": (90, 90)}, 9: {"speaking": (84, 88), "writing": (88, 89)},
#     8: {"speaking": (76, 83), "writing": (79, 87)}, 7: {"speaking": (68, 75), "writing": (69, 78)},
#     6: {"speaking": (59, 67), "writing": (60, 68)}, 5: {"speaking": (51, 58), "writing": (51, 59)},
#     4: {"speaking": (42, 50), "writing": (41, 50)}, 3: {"speaking": (34, 41), "writing": (32, 40)}
# }

# speaking_tasks = [
#     "read_aloud", "repeat_sentence", "describe_image", "retell_lecture",
#     "answer_short_question", "respond_to_a_situation",
#     "summarize_group_discussion"
# ]
# writing_tasks = ["summarize_written_text", "write_email", "write_essay"]

# # =============================
# # Pydantic Model
# # =============================
# class EvaluationRequest(BaseModel):
#     exam_type: str
#     user_id: str
#     test_id: str
#     responses: List[Dict[str, Any]]

# # =============================
# # Internal Helper for Score Normalization
# # This function now assumes all evaluators return a 10-90 PTE scaled 'overall_score'.
# # =============================
# def _get_normalized_score_for_averaging(evaluation_result_dict: Dict[str, Any], question_type: str) -> float:
#     """
#     Extracts the 'overall_score' directly from an evaluator's result.
#     Assumes the evaluator has already scaled the score to the 10-90 PTE range.
#     """
#     score = evaluation_result_dict.get("overall_score")
#     if score is None:
#         logger.error(f"Evaluator for '{question_type}' did not return an 'overall_score'. Defaulting to 10.0.")
#         return 10.0 # Default to minimum PTE score if not found
    
#     # Ensure it's a float and within bounds, though evaluators should handle this.
#     try:
#         score_float = float(score)
#         # This clamping is largely defensive, as evaluators should return 10-90 already.
#         return max(10.0, min(90.0, score_float))
#     except (ValueError, TypeError):
#         logger.error(f"Evaluator for '{question_type}' returned non-numeric 'overall_score': {score}. Defaulting to 10.0.")
#         return 10.0

# # =============================
# # API Endpoints
# # =============================
# @app.route("/evaluate-test-paper", methods=["POST"])
# def evaluate_test_paper():
#     req_data = None
#     files_data = {} # To store uploaded files

#     content_type = request.headers.get('Content-Type', '')
#     if content_type.startswith('application/json'):
#         try:
#             req_data = request.get_json()
#         except Exception as e:
#             logger.error(f"Invalid JSON format: {e}")
#             return jsonify({"error": "Invalid JSON format", "details": str(e)}), 400
#     elif content_type.startswith('multipart/form-data'):
#         json_payload_str = request.form.get('data')
#         if not json_payload_str:
#             logger.error("Missing 'data' field in multipart/form-data request.")
#             return jsonify({"error": "Missing 'data' field in multipart/form-data"}), 400
#         try:
#             req_data = json.loads(json_payload_str)
#         except json.JSONDecodeError as e:
#             logger.error(f"Invalid JSON in 'data' field of form-data: {e}")
#             return jsonify({"error": "Invalid JSON in 'data' field", "details": str(e)}), 400
        
#         files_data = request.files # Get all uploaded files
#     else:
#         logger.error(f"Unsupported Content-Type: {content_type}")
#         return jsonify({"error": "Unsupported Content-Type", "details": "Please use application/json or multipart/form-data"}), 415

#     try:
#         req = EvaluationRequest(**req_data)
#     except ValidationError as e:
#         logger.error(f"Invalid request format (Pydantic): {e.errors()}")
#         return jsonify({"error": "Invalid request format", "details": e.errors()}), 400

#     if not collection.find_one({"test_id": req.test_id}):
#         logger.error(f"Test paper with test_id {req.test_id} not found")
#         return jsonify({"error": f"Test paper with test_id {req.test_id} not found"}), 404

#     exam_type = req.exam_type.lower()
#     if exam_type not in TASK_PATTERN_MAP:
#         logger.error(f"Invalid exam_type: {exam_type}")
#         return jsonify({"error": f"Invalid exam_type provided: {exam_type}"}), 400

#     expected_tasks = TASK_PATTERN_MAP[exam_type]
#     submitted_q_types = [r.get("question_type") for r in req.responses]
    
#     for task_spec in expected_tasks:
#         task_name = task_spec["task"]
#         expected_count = task_spec["count"]
#         actual_count = submitted_q_types.count(task_name)
#         if actual_count != expected_count:
#             error_msg = f"Task count mismatch for {task_name}: expected {expected_count}, but got {actual_count}"
#             logger.error(error_msg)
#             return jsonify({"error": error_msg}), 400

#     evaluated_responses = defaultdict(list)
#     speaking_scores = []
#     writing_scores = []

#     for response in req.responses:
#         q_type = response.get("question_type")
        
#         if q_type == "personal_introduction":
#             logger.info(f"Skipping formal evaluation for 'personal_introduction' (test_id: {req.test_id}, user_id: {req.user_id}).")
#             evaluated_responses[q_type].append({
#                 "question": response.get("questions", [{}])[0].get("instruction"),
#                 "user_response": response.get("user_response"),
#                 "evaluation": {"message": "Personal introduction is not formally scored.", "overall_score": 0}
#             })
#             continue

#         if q_type not in EVALUATOR_MAP:
#             logger.warning(f"Unknown question_type received: {q_type}, skipping.")
#             continue

#         input_field = PROMPT_TYPE_TO_INPUT_FIELD.get(q_type)
#         questions_list = response.get("questions")

#         question_prompt_content = None
#         if questions_list and isinstance(questions_list, list) and len(questions_list) > 0:
#             question_details = questions_list[0]
#             question_prompt_content = question_details.get(input_field)
        
#         user_response_payload = response.get("user_response")

#         if question_prompt_content is None and q_type not in ["summarize_group_discussion"]: # S.G.D handles prompt differently
#              logger.error(f"Missing question prompt content for {q_type}. Question details: {questions_list[0] if questions_list else 'N/A'}")
#              return jsonify({"error": f"Missing question prompt content for {q_type}"}), 400
        
#         if user_response_payload is None:
#             logger.error(f"Missing user_response for {q_type}")
#             return jsonify({"error": f"Missing user_response for {q_type}"}), 400

#         user_response_for_evaluator_arg = user_response_payload 
        
#         # Special handling for audio-based tasks and tasks with complex prompt structures
#         if q_type == "summarize_group_discussion":
#             audio_bytes_data = None
#             if content_type.startswith('multipart/form-data') and isinstance(user_response_payload, str) and user_response_payload in files_data:
#                 audio_file = files_data[user_response_payload]
#                 try:
#                     audio_bytes_data = audio_file.read()
#                     logger.info(f"Successfully processed uploaded audio file '{user_response_payload}' for {q_type}.")
#                 except Exception as e:
#                     logger.error(f"Error reading uploaded audio file '{user_response_payload}' for {q_type}: {e}")
#                     return jsonify({"error": f"Failed to process uploaded audio file '{user_response_payload}' for {q_type}"}), 500
#             elif content_type.startswith('application/json') and isinstance(user_response_payload, str):
#                 try:
#                     audio_bytes_data = base64.b64decode(user_response_payload)
#                     logger.info(f"Successfully decoded base64 audio string for {q_type} from JSON payload.")
#                 except Exception as e:
#                     logger.error(f"Error decoding base64 audio string for {q_type}: {e}")
#                     return jsonify({"error": f"Invalid base64 audio data for {q_type}"}), 400
#             else:
#                 logger.error(f"Invalid or missing audio data for {q_type}. Expected file key in form-data or base64 string in JSON.")
#                 return jsonify({"error": f"Invalid audio data for {q_type}"}), 400
            
#             if audio_bytes_data is None:
#                 return jsonify({"error": f"Audio data could not be processed for {q_type}"}), 500
            
#             user_response_for_evaluator_arg = audio_bytes_data

#         evaluator = EVALUATOR_MAP[q_type]()
        
#         # Dispatch to appropriate evaluator.evaluate method based on q_type
#         if q_type == "summarize_group_discussion":
#             evaluation_result = evaluator.evaluate(
#                 discussion_data=question_details.get("discussion"),
#                 audio_file_stream=user_response_for_evaluator_arg,
#                 topic=question_details.get("topic") # Pass the topic
#             )
#         elif q_type == "retell_lecture":
#             # Renamed 'prompt' to 'lecture_content' in evaluator's method, so using 'lecture' from question_details
#             evaluation_result = evaluator.evaluate(question_details.get("lecture"), user_response_for_evaluator_arg)
#         elif q_type == "write_email":
#             # Renamed 'prompt' to 'task' in evaluator's method, so using 'task' from question_details
#             evaluation_result = evaluator.evaluate(question_details.get("task"), user_response_for_evaluator_arg)
#         elif q_type == "write_essay":
#             # Renamed 'prompt' to 'topic' in evaluator's method, so using 'topic' from question_details
#             evaluation_result = evaluator.evaluate(question_details.get("topic"), user_response_for_evaluator_arg)
#         elif q_type == "summarize_written_text":
#             # Renamed 'prompt' to 'passage_content' in evaluator's method, so using 'passage' from question_details
#             evaluation_result = evaluator.evaluate(question_details.get("passage"), user_response_for_evaluator_arg)
#         else:
#             # This 'else' block handles: read_aloud, repeat_sentence, describe_image,
#             # answer_short_question, respond_to_a_situation.
#             # Their `evaluate` methods expect `(prompt_string, user_response_string)`.
#             evaluation_result = evaluator.evaluate(question_prompt_content, user_response_for_evaluator_arg)

#         # Extract and normalize the score to a 0-90 scale for consistent averaging
#         # This function now simply gets the already scaled score (10-90).
#         score = _get_normalized_score_for_averaging(evaluation_result, q_type)

#         if q_type in speaking_tasks:
#             speaking_scores.append(score)
#         elif q_type in writing_tasks:
#             writing_scores.append(score)

#         evaluated_responses[q_type].append({
#             "question": question_prompt_content,
#             "user_response": user_response_payload,
#             "evaluation": evaluation_result # Store the full, raw evaluation result
#         })

#     avg_speaking = sum(speaking_scores) / len(speaking_scores) if speaking_scores else 0
#     avg_writing = sum(writing_scores) / len(writing_scores) if writing_scores else 0
  
#     avg_speaking_for_clb = round(avg_speaking)
#     avg_writing_for_clb = round(avg_writing)

#     clb_speaking, clb_writing = None, None
#     for level in sorted(CLB_MAPPING.keys(), reverse=True):
#         ranges = CLB_MAPPING[level]
#         if clb_speaking is None and ranges["speaking"][0] <= avg_speaking_for_clb <= ranges["speaking"][1]:
#             clb_speaking = level
#         if clb_writing is None and ranges["writing"][0] <= avg_writing_for_clb <= ranges["writing"][1]:
#             clb_writing = level
#         if clb_speaking is not None and clb_writing is not None:
#             break
    
#     min_speaking_clb_score = min(r["speaking"][0] for r in CLB_MAPPING.values()) if CLB_MAPPING else 0
#     min_writing_clb_score = min(r["writing"][0] for r in CLB_MAPPING.values()) if CLB_MAPPING else 0

#     if clb_speaking is None and speaking_scores and avg_speaking_for_clb < min_speaking_clb_score:
#         clb_speaking = 0
#     if clb_writing is None and writing_scores and avg_writing_for_clb < min_writing_clb_score:
#         clb_writing = 0

#     overall_score_summary = {
#         "average_speaking_score": round(avg_speaking, 2),
#         "average_writing_score": round(avg_writing, 2),
#         "clb_speaking": clb_speaking,
#         "clb_writing": clb_writing,
#         "overall_feedback": f"Evaluation completed for {req.exam_type} mode. {len(req.responses)} responses were processed successfully.",
#         "evaluated_at": datetime.utcnow().isoformat()
#     }

#     update_payload = {
#         "status": "completed",
#         "overall_score": overall_score_summary,
#         **{qt: evaluated_responses[qt] for qt in evaluated_responses}
#     }

#     try:
#         collection.update_one(
#             {"test_id": req.test_id},
#             {"$set": update_payload}
#         )
#         logger.info(f"Successfully updated evaluation for test_id {req.test_id}")
      
#         updated_document = collection.find_one({"test_id": req.test_id}, {"_id": 0})
#         return jsonify(updated_document)

#     except Exception as e:
#         logger.error(f"Failed to update MongoDB for test_id {req.test_id}: {e}", exc_info=True)
#         return jsonify({"error": "Failed to update database", "details": str(e)}), 500

# @app.route("/")
# def home():
#     return jsonify({
#         "message": "Welcome to PTE Evaluator API!",
#         "endpoint": "/evaluate-test-paper"
#     })

# if __name__ == "__main__":
#     logger.info("🚀 Starting Flask PTE Evaluator API on http://localhost:7010")
#     app.run(host="0.0.0.0", port=7010)


# import sys
# import os
# import logging
# import json
# import base64
# from datetime import datetime
# import functools # For wrapping logger

# # Add the project's source directory to the Python path.
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # =============================
# # Setup Central Logger
# # =============================
# # Configure logging to write all terminal output to evaluation.log
# log_file_path = "evaluation.log"

# logging.basicConfig(
#     filename=log_file_path,
#     filemode="a",  # 'a' for append
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO, # Changed to INFO to reduce verbosity by default
#     force=True  # This overrides any default handlers to ensure all logs are captured
# )

# # Create a logger instance for this module
# logger = logging.getLogger(__name__)

# # Redirect stdout and stderr to the logger to capture everything
# class StreamToLogger:
#     """
#     Fake file-like stream object that redirects writes to a logger instance.
#     """
#     def __init__(self, logger_name, level):
#         self.logger = logging.getLogger(logger_name)
#         self.level = level
#         self._write_func = functools.partial(self.logger.log, self.level)

#     def write(self, buf):
#         for line in buf.rstrip().splitlines():
#             if line:
#                 self._write_func(line.rstrip())

#     def flush(self):
#         pass

# sys.stdout = StreamToLogger('STDOUT', logging.INFO)
# sys.stderr = StreamToLogger('STDERR', logging.WARNING)

# logger.info("=========================================================")
# logger.info("           Application starting up...                    ")
# logger.info("=========================================================")

# # Set higher logging levels for noisy external libraries
# logging.getLogger('pymongo.topology').setLevel(logging.WARNING)
# logging.getLogger('pymongo.serverSelection').setLevel(logging.WARNING)
# logging.getLogger('pymongo.connection').setLevel(logging.WARNING)
# logging.getLogger('pymongo.command').setLevel(logging.WARNING)

# logging.getLogger('openai._base_client').setLevel(logging.WARNING)
# logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
# logging.getLogger('httpcore.http11').setLevel(logging.WARNING)
# logging.getLogger('httpx').setLevel(logging.INFO)

# logging.getLogger('numba.core.byteflow').setLevel(logging.ERROR)
# logging.getLogger('numba.core.ssa').setLevel(logging.ERROR)
# logging.getLogger('numba.core.interpreter').setLevel(logging.ERROR)
# logging.getLogger('numba').setLevel(logging.ERROR)

import sys
import os
import logging
import json
import base64
from datetime import datetime
import functools # For wrapping logger

# Add the project's source directory to the Python path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# =============================
# Setup Central Logger (FIXED)
# =============================
log_file_path = "evaluation.log"

# Create root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# -------- File Handler (evaluation.log) --------
file_handler = logging.FileHandler(log_file_path, mode="a")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.INFO)

# -------- Stream Handler (Docker stdout) --------
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(file_formatter)
stream_handler.setLevel(logging.INFO)

# -------- Apply Handlers --------
logger.handlers.clear()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info("=========================================================")
logger.info("           Application starting up...                    ")
logger.info("=========================================================")

# =============================
# Suppress noisy external logs
# =============================
logging.getLogger('pymongo.topology').setLevel(logging.WARNING)
logging.getLogger('pymongo.serverSelection').setLevel(logging.WARNING)
logging.getLogger('pymongo.connection').setLevel(logging.WARNING)
logging.getLogger('pymongo.command').setLevel(logging.WARNING)

logging.getLogger('openai._base_client').setLevel(logging.WARNING)
logging.getLogger('httpcore.connection').setLevel(logging.WARNING)
logging.getLogger('httpcore.http11').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.INFO)

logging.getLogger('numba.core.byteflow').setLevel(logging.ERROR)
logging.getLogger('numba.core.ssa').setLevel(logging.ERROR)
logging.getLogger('numba.core.interpreter').setLevel(logging.ERROR)
logging.getLogger('numba').setLevel(logging.ERROR)

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
from collections import defaultdict
import pymongo
from config import settings

# Import evaluators (ensure these paths are correct for your project structure)
from evaluators.describe_image_evaluator import DescribeImageEvaluator
from evaluators.read_aloud_evaluator import ReadAloudEvaluator
from evaluators.retell_lecture_evaluator import RetellLectureEvaluator
from evaluators.answer_short_question_evaluator import AnswerShortQuestionEvaluator
from evaluators.repeat_sentence_evaluator import RepeatSentenceEvaluator
from evaluators.write_email_evaluator import WriteEmailEvaluator
from evaluators.write_essay_evaluator import WriteEssayEvaluator
from evaluators.summarize_written_text_evaluator import SummarizeWrittenTextEvaluator
from evaluators.respond_to_a_situation_evaluator import RespondToASituationEvaluator
from evaluators.summarize_group_discussion_evaluator import SummarizeGroupDiscussionEvaluator


# =============================
# Initialize App & DB
# =============================
app = Flask(__name__)
CORS(app)

mongo_client = pymongo.MongoClient(settings.MONGO_URI)
db = mongo_client["pte_speaking_writing_database"]
collection = db["speaking_writing"]

# =============================
# Mappings and Constants
# =============================
EVALUATOR_MAP = {
    "describe_image": DescribeImageEvaluator,
    "read_aloud": ReadAloudEvaluator,
    "retell_lecture": RetellLectureEvaluator,
    "answer_short_question": AnswerShortQuestionEvaluator,
    "repeat_sentence": RepeatSentenceEvaluator,
    "write_email": WriteEmailEvaluator,
    "write_essay": WriteEssayEvaluator,
    "summarize_written_text": SummarizeWrittenTextEvaluator,
    "respond_to_a_situation": RespondToASituationEvaluator,
    "summarize_group_discussion": SummarizeGroupDiscussionEvaluator
}

PROMPT_TYPE_TO_INPUT_FIELD = {
    "read_aloud": "paragraph", "repeat_sentence": "sentence", "describe_image": "description",
    "respond_to_a_situation": "situation", "retell_lecture": "lecture",
    "answer_short_question": "question", "summarize_written_text": "passage",
    "write_email": "task", "write_essay": "topic",
    "summarize_group_discussion": "discussion" # Note: 'discussion' here refers to the list of speaker dialogues.
}

TASK_PATTERN_MAP = {
    "core": [
        {"task": "read_aloud", "count": 6}, {"task": "repeat_sentence", "count": 10},
        {"task": "describe_image", "count": 3}, {"task": "respond_to_a_situation", "count": 3},
        {"task": "answer_short_question", "count": 6}, {"task": "summarize_written_text", "count": 1},
        {"task": "write_email", "count": 2}
    ],
    "academic": [
        {"task": "read_aloud", "count": 1}, {"task": "repeat_sentence", "count": 1},
        {"task": "describe_image", "count": 1}, {"task": "retell_lecture", "count": 1},
        {"task": "answer_short_question", "count": 1},{"task": "summarize_group_discussion", "count": 1},
        {"task": "respond_to_a_situation", "count": 1}, {"task": "summarize_written_text", "count": 1},
        {"task": "write_essay", "count": 1}
    ]
}

CLB_MAPPING = {
    10: {"speaking": (89, 90), "writing": (90, 90)}, 9: {"speaking": (84, 88), "writing": (88, 89)},
    8: {"speaking": (76, 83), "writing": (79, 87)}, 7: {"speaking": (68, 75), "writing": (69, 78)},
    6: {"speaking": (59, 67), "writing": (60, 68)}, 5: {"speaking": (51, 58), "writing": (51, 59)},
    4: {"speaking": (42, 50), "writing": (41, 50)}, 3: {"speaking": (34, 41), "writing": (32, 40)}
}

speaking_tasks = [
    "read_aloud", "repeat_sentence", "describe_image", "retell_lecture",
    "answer_short_question", "respond_to_a_situation",
    "summarize_group_discussion"
]
writing_tasks = ["summarize_written_text", "write_email", "write_essay"]

# =============================
# Pydantic Model
# =============================
class EvaluationRequest(BaseModel):
    exam_type: str
    user_id: str
    test_id: str
    responses: List[Dict[str, Any]]

# =============================
# Internal Helper for Score Normalization
# This function now assumes all evaluators return a 10-90 PTE scaled 'overall_score'.
# =============================
def _get_normalized_score_for_averaging(evaluation_result_dict: Dict[str, Any], question_type: str) -> float:
    """
    Extracts the 'overall_score' directly from an evaluator's result.
    Assumes the evaluator has already scaled the score to the 10-90 PTE range.
    """
    score = evaluation_result_dict.get("overall_score")
    if score is None:
        logger.error(f"Evaluator for '{question_type}' did not return an 'overall_score'. Defaulting to 10.0.")
        return 10.0 # Default to minimum PTE score if not found
    
    # Ensure it's a float and within bounds, though evaluators should handle this.
    try:
        score_float = float(score)
        # This clamping is largely defensive, as evaluators should return 10-90 already.
        return max(10.0, min(90.0, score_float))
    except (ValueError, TypeError):
        logger.error(f"Evaluator for '{question_type}' returned non-numeric 'overall_score': {score}. Defaulting to 10.0.")
        return 10.0

# =============================
# API Endpoints
# =============================
@app.route("/evaluate-test-paper", methods=["POST"])
def evaluate_test_paper():
    req_data = None
    files_data = {} # To store uploaded files

    content_type = request.headers.get('Content-Type', '')
    if content_type.startswith('application/json'):
        try:
            req_data = request.get_json()
        except Exception as e:
            logger.error(f"Invalid JSON format: {e}")
            return jsonify({"error": "Invalid JSON format", "details": str(e)}), 400
    elif content_type.startswith('multipart/form-data'):
        json_payload_str = request.form.get('data')
        if not json_payload_str:
            logger.error("Missing 'data' field in multipart/form-data request.")
            return jsonify({"error": "Missing 'data' field in multipart/form-data"}), 400
        try:
            req_data = json.loads(json_payload_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in 'data' field of form-data: {e}")
            return jsonify({"error": "Invalid JSON in 'data' field", "details": str(e)}), 400
        
        files_data = request.files # Get all uploaded files
    else:
        logger.error(f"Unsupported Content-Type: {content_type}")
        return jsonify({"error": "Unsupported Content-Type", "details": "Please use application/json or multipart/form-data"}), 415

    try:
        req = EvaluationRequest(**req_data)
    except ValidationError as e:
        logger.error(f"Invalid request format (Pydantic): {e.errors()}")
        return jsonify({"error": "Invalid request format", "details": e.errors()}), 400

    if not collection.find_one({"test_id": req.test_id}):
        logger.error(f"Test paper with test_id {req.test_id} not found")
        return jsonify({"error": f"Test paper with test_id {req.test_id} not found"}), 404

    exam_type = req.exam_type.lower()
    if exam_type not in TASK_PATTERN_MAP:
        logger.error(f"Invalid exam_type: {exam_type}")
        return jsonify({"error": f"Invalid exam_type provided: {exam_type}"}), 400

    expected_tasks = TASK_PATTERN_MAP[exam_type]
    submitted_q_types = [r.get("question_type") for r in req.responses]
    
    for task_spec in expected_tasks:
        task_name = task_spec["task"]
        expected_count = task_spec["count"]
        actual_count = submitted_q_types.count(task_name)
        if actual_count != expected_count:
            error_msg = f"Task count mismatch for {task_name}: expected {expected_count}, but got {actual_count}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400

    evaluated_responses = defaultdict(list)
    speaking_scores = []
    writing_scores = []

    for response in req.responses:
        q_type = response.get("question_type")
        
        if q_type == "personal_introduction":
            logger.info(f"Skipping formal evaluation for 'personal_introduction' (test_id: {req.test_id}, user_id: {req.user_id}).")
            evaluated_responses[q_type].append({
                "question": response.get("questions", [{}])[0].get("instruction"),
                "user_response": response.get("user_response"),
                "evaluation": {"message": "Personal introduction is not formally scored.", "overall_score": 0}
            })
            continue

        if q_type not in EVALUATOR_MAP:
            logger.warning(f"Unknown question_type received: {q_type}, skipping.")
            continue

        input_field = PROMPT_TYPE_TO_INPUT_FIELD.get(q_type)
        questions_list = response.get("questions")

        question_prompt_content = None
        if questions_list and isinstance(questions_list, list) and len(questions_list) > 0:
            question_details = questions_list[0]
            question_prompt_content = question_details.get(input_field)
        
        user_response_payload = response.get("user_response")

        # It's okay for question_prompt_content to be None for summarize_group_discussion
        # as it uses 'discussion' and 'topic' directly from question_details.
        # For other tasks expecting a string prompt, it must be present.
        if question_prompt_content is None and q_type not in ["summarize_group_discussion"]:
             logger.error(f"Missing question prompt content for {q_type}. Question details: {questions_list[0] if questions_list else 'N/A'}")
             return jsonify({"error": f"Missing question prompt content for {q_type}"}), 400
        
        if user_response_payload is None:
            logger.error(f"Missing user_response for {q_type}")
            return jsonify({"error": f"Missing user_response for {q_type}"}), 400

        user_response_for_evaluator_arg = user_response_payload 
        
        # Special handling for audio-based tasks and tasks with complex prompt structures
        if q_type == "summarize_group_discussion":
            audio_bytes_data = None
            if content_type.startswith('multipart/form-data') and isinstance(user_response_payload, str) and user_response_payload in files_data:
                audio_file = files_data[user_response_payload]
                try:
                    audio_bytes_data = audio_file.read()
                    logger.info(f"Successfully processed uploaded audio file '{user_response_payload}' for {q_type}.")
                except Exception as e:
                    logger.error(f"Error reading uploaded audio file '{user_response_payload}' for {q_type}: {e}")
                    return jsonify({"error": f"Failed to process uploaded audio file '{user_response_payload}' for {q_type}"}), 500
            elif content_type.startswith('application/json') and isinstance(user_response_payload, str):
                try:
                    audio_bytes_data = base64.b64decode(user_response_payload)
                    logger.info(f"Successfully decoded base64 audio string for {q_type} from JSON payload.")
                except Exception as e:
                    logger.error(f"Error decoding base64 audio string for {q_type}: {e}")
                    return jsonify({"error": f"Invalid base64 audio data for {q_type}"}), 400
            else:
                logger.error(f"Invalid or missing audio data for {q_type}. Expected file key in form-data or base64 string in JSON.")
                return jsonify({"error": f"Invalid audio data for {q_type}"}), 400
            
            if audio_bytes_data is None:
                return jsonify({"error": f"Audio data could not be processed for {q_type}"}), 500
            
            user_response_for_evaluator_arg = audio_bytes_data

        evaluator = EVALUATOR_MAP[q_type]()
        
        # Dispatch to appropriate evaluator.evaluate method based on q_type
        if q_type == "summarize_group_discussion":
            # Passes discussion_data, audio_file_stream, and topic
            evaluation_result = evaluator.evaluate(
                discussion_data=question_details.get("discussion"),
                audio_file_stream=user_response_for_evaluator_arg,
                topic=question_details.get("topic")
            )
        elif q_type == "retell_lecture":
            # Expects (lecture_content: str, user_response: str)
            evaluation_result = evaluator.evaluate(question_details.get("lecture"), user_response_for_evaluator_arg)
        elif q_type == "write_email":
            # Expects (prompt: str, user_response: str)
            evaluation_result = evaluator.evaluate(question_details.get("task"), user_response_for_evaluator_arg)
        elif q_type == "write_essay":
            # Expects (prompt: str, user_response: str)
            evaluation_result = evaluator.evaluate(question_details.get("topic"), user_response_for_evaluator_arg)
        elif q_type == "summarize_written_text":
            # Expects (passage_content: str, user_response: str)
            evaluation_result = evaluator.evaluate(question_details.get("passage"), user_response_for_evaluator_arg)
        else:
            # This 'else' block handles: read_aloud, repeat_sentence, describe_image,
            # answer_short_question, respond_to_a_situation.
            # Their `evaluate` methods expect `(prompt_string, user_response_string)`.
            evaluation_result = evaluator.evaluate(question_prompt_content, user_response_for_evaluator_arg)

        # Extract and normalize the score to a 0-90 scale for consistent averaging
        # This function now simply gets the already scaled score (10-90).
        score = _get_normalized_score_for_averaging(evaluation_result, q_type)

        if q_type in speaking_tasks:
            speaking_scores.append(score)
        elif q_type in writing_tasks:
            writing_scores.append(score)

        evaluated_responses[q_type].append({
            # Store original prompt content; for summarize_group_discussion this will be None,
            # but the full discussion_data is also available in question_details.
            "question": question_prompt_content, 
            "user_response": user_response_payload, # Store original user response
            "evaluation": evaluation_result # Store the full, raw evaluation result
        })

    avg_speaking = sum(speaking_scores) / len(speaking_scores) if speaking_scores else 0
    avg_writing = sum(writing_scores) / len(writing_scores) if writing_scores else 0
  
    avg_speaking_for_clb = round(avg_speaking)
    avg_writing_for_clb = round(avg_writing)

    clb_speaking, clb_writing = None, None
    for level in sorted(CLB_MAPPING.keys(), reverse=True):
        ranges = CLB_MAPPING[level]
        if clb_speaking is None and ranges["speaking"][0] <= avg_speaking_for_clb <= ranges["speaking"][1]:
            clb_speaking = level
        if clb_writing is None and ranges["writing"][0] <= avg_writing_for_clb <= ranges["writing"][1]:
            clb_writing = level
        if clb_speaking is not None and clb_writing is not None:
            break
    
    min_speaking_clb_score = min(r["speaking"][0] for r in CLB_MAPPING.values()) if CLB_MAPPING else 0
    min_writing_clb_score = min(r["writing"][0] for r in CLB_MAPPING.values()) if CLB_MAPPING else 0

    if clb_speaking is None and speaking_scores and avg_speaking_for_clb < min_speaking_clb_score:
        clb_speaking = 0
    if clb_writing is None and writing_scores and avg_writing_for_clb < min_writing_clb_score:
        clb_writing = 0

    overall_score_summary = {
        "average_speaking_score": round(avg_speaking, 2),
        "average_writing_score": round(avg_writing, 2),
        "clb_speaking": clb_speaking,
        "clb_writing": clb_writing,
        "overall_feedback": f"Evaluation completed for {req.exam_type} mode. {len(req.responses)} responses were processed successfully.",
        "evaluated_at": datetime.utcnow().isoformat()
    }

    update_payload = {
        "status": "completed",
        "overall_score": overall_score_summary,
        **{qt: evaluated_responses[qt] for qt in evaluated_responses}
    }

    try:
        collection.update_one(
            {"test_id": req.test_id},
            {"$set": update_payload}
        )
        logger.info(f"Successfully updated evaluation for test_id {req.test_id}")
      
        updated_document = collection.find_one({"test_id": req.test_id}, {"_id": 0})
        return jsonify(updated_document)

    except Exception as e:
        logger.error(f"Failed to update MongoDB for test_id {req.test_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to update database", "details": str(e)}), 500

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to PTE Evaluator API!",
        "endpoint": "/evaluate-test-paper"
    })

if __name__ == "__main__":
    logger.info("🚀 Starting Flask PTE Evaluator API on http://localhost:7010")
    app.run(host="0.0.0.0", port=7010)