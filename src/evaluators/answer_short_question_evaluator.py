# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re

# class AnswerShortQuestionEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Clean up user response
#         user_response = user_response.strip()

#         # Word count
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count > 3:
#             word_count_feedback = f"⚠️ Your answer has {word_count} words. Keep answers concise — ideally 1–3 words."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         # Spell Check
#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             misspelled_words = [word for word in blob.words if word != TextBlob(word).correct()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(misspelled_words)}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # Gemini Prompt
#         instruction = f"""
# You are a PTE expert evaluating the "Answer Short Question" task.

# Question: {prompt}
# User Said: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Accuracy: Is the answer factually correct?
# - Grammar: Sentence structure accuracy
# - Relevance: Does the response directly answer the question?

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "accuracy": <number>,
#     "grammar": <number>,
#     "relevance": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """

#         result = self._get_openai_score(instruction)

#         # Optional: Apply weighted average
#         if "scores" in result:
#             scores = result["scores"]
#             weights = {
#                 "accuracy": 0.70,
#                 "grammar": 0.15,
#                 "relevance": 0.15
#             }

#             overall = sum(scores[k] * weights.get(k, 0) for k in scores if k in weights)
#             result["overall_score"] = round(overall, 1)

#         # Append additional feedback
#         additional_feedback = []
#         if "feedback" in result:
#             additional_feedback.append(result["feedback"])
#         additional_feedback.append(word_count_feedback)
#         additional_feedback.append(spell_check_feedback)

#         result["feedback"] = "\n".join(additional_feedback)

#         return result

# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging

# # Get a logger instance for this module (important for proper log organization)
# logger = logging.getLogger(__name__)

# class AnswerShortQuestionEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Clean up user response
#         user_response = user_response.strip()

#         # --- Automated Feedback Generation ---
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE ASQ typically expects 1-3 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please provide an answer."
#         elif word_count > 3:
#             word_count_feedback = f"⚠️ Your answer has {word_count} words. Keep answers concise — ideally 1–3 words for Answer Short Question."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         # Spell Check
#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Compare lowercase versions to ignore case differences when checking spelling
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
#             if misspelled_words:
#                 # Use a set and sort to ensure unique and ordered misspelled words for clean display
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             # Log the exception for debugging
#             logger.error(f"Error during spell check for AnswerShortQuestion: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- LLM Instruction (Prompt) Preparation ---
#         # Using double curly braces {{ and }} for literal JSON curly braces inside the f-string.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Answer Short Question" task.
# For this task, the most critical aspect is providing the *single most appropriate* and *factually correct* answer, usually in 1-3 words. Grammar is less critical than accuracy for scoring, but good grammar enhances clarity.

# Question: {prompt}
# User Said: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Accuracy: Does the response provide the single most appropriate and factually correct answer to the question?
# - Grammar: Is the sentence structure accurate? (Less critical for ASQ, but still considered for overall quality)
# - Relevance: Does the response directly and precisely answer the question without additional irrelevant information?

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "accuracy": <number>,
#     "grammar": <number>,
#     "relevance": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """

#         # --- Call BaseEvaluator for LLM Score ---
#         # The LLM prompt explicitly asks for scores on a 0-90 scale and provides "scores" and "overall_score" keys.
#         # We define a mapping to tell BaseEvaluator where to find these in the raw LLM output.
#         score_key_map = {
#             "accuracy": {"key": "scores.accuracy"},
#             "grammar": {"key": "scores.grammar"},
#             "relevance": {"key": "scores.relevance"}
#         }
#         overall_score_key = "overall_score" # The LLM's top-level key for the overall score

#         # _get_openai_score will now handle LLM call, retries, JSON parsing,
#         # score extraction, normalization, and clamping to 10-90 range automatically.
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             # Since the LLM is instructed to return 0-90, its native scale matches PTE.
#             default_llm_output_max_scale=90
#         )

#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         # Start with the feedback provided directly by the LLM
#         if processed_result.get("feedback"):
#             final_feedback_parts.append(processed_result["feedback"])
        
#         # Add automated feedback after LLM's comments
#         final_feedback_parts.append(word_count_feedback)
#         final_feedback_parts.append(spell_check_feedback)

#         # Join feedback, filtering out empty strings to avoid extra blank lines
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are already guaranteed to be floats within 10.0-90.0 range.
#         scores_for_log = processed_result.get("scores", {})
#         accuracy = scores_for_log.get("accuracy", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         relevance = scores_for_log.get("relevance", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(f"AnswerShortQuestion Evaluation: Overall={overall:.2f} (Accuracy: {accuracy:.2f}, Grammar: {grammar:.2f}, Relevance: {relevance:.2f})")

#         return processed_result


## src/evaluators/answer_short_question_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
from textblob import TextBlob
import re
import logging

logger = logging.getLogger(__name__)

class AnswerShortQuestionEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Answer Short Question task.
    Uses an LLM for scoring Accuracy, Grammar, and Relevance.
    Integrates preprocessing for word count and spell check.
    """
    def __init__(self):
        super().__init__()
        # Define the raw scale the LLM is expected to output for each trait.
        # The prompt asks for 0-90, and LLMs usually try to follow this.
        self.trait_definitions = {
            "accuracy": {"llm_output_max_scale": 90},
            "grammar": {"llm_output_max_scale": 90},
            "relevance": {"llm_output_max_scale": 90},
            # overall_score is also 0-90 as defined by PTE
            "overall_score": {"llm_output_max_scale": 90} 
        }

    def evaluate(self, prompt: str, user_response: str) -> dict:
        logger.debug("--- AnswerShortQuestionEvaluator: Starting evaluation ---")
        user_response = user_response.strip()

        # --- Automated Feedback Generation ---
        word_count = len(user_response.split())
        word_count_feedback = ""

        if word_count == 0:
            word_count_feedback = "⚠️ Your response is empty. Please provide an answer."
        elif word_count > 3:
            word_count_feedback = f"⚠️ Your answer has {word_count} words. Keep answers concise — ideally 1–3 words for Answer Short Question."
        else:
            word_count_feedback = "✅ Response length is appropriate."

        spell_check_feedback = ""
        try:
            blob = TextBlob(user_response)
            misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
            if misspelled_words:
                spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
            else:
                spell_check_feedback = "✅ Spelling appears correct."
        except Exception as e:
            logger.error(f"Error during spell check for AnswerShortQuestion: {e}", exc_info=True)
            spell_check_feedback = "Spell check skipped due to technical issue."

        # --- LLM Instruction (Prompt) Preparation ---
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Answer Short Question" task.
For this task, the most critical aspect is providing the *single most appropriate* and *factually correct* answer, usually in 1-3 words. Grammar is less critical than accuracy for scoring, but good grammar enhances clarity.

Question: {prompt}
User Said: {user_response}

Additional Info for your consideration (these are observations, not scores from you directly):
- {word_count_feedback}
- {spell_check_feedback}
- Word Count: {word_count}

Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
- Accuracy: Does the response provide the single most appropriate and factually correct answer to the question? (0-90)
- Grammar: Is the sentence structure accurate? (Less critical for ASQ, but still considered for overall quality) (0-90)
- Relevance: Does the response directly and precisely answer the question without additional irrelevant information? (0-90)

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"AnswerShortQuestion LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

        # --- Call BaseEvaluator for LLM Score ---
        score_key_map = {
            "accuracy": {"key": "scores.accuracy", "llm_output_max_scale": self.trait_definitions['accuracy']['llm_output_max_scale']},
            "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
            "relevance": {"key": "scores.relevance", "llm_output_max_scale": self.trait_definitions['relevance']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=90,
            default_feedback_message="The AI model could not process your answer for Answer Short Question due to an internal error or connection issue. Please try again." # More specific default feedback
        )

        # --- Combine LLM Feedback with Automated Feedback ---
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        
        # Only add automated feedback if LLM processed correctly or if LLM didn't provide specific feedback
        if processed_result.get("overall_score", 0) > 10.0 or not processed_result.get("feedback"):
             final_feedback_parts.append(word_count_feedback)
             final_feedback_parts.append(spell_check_feedback)

        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        # --- Logging Final Scores (Crucial for debugging and verification) ---
        scores_for_log = processed_result.get("scores", {})
        accuracy = scores_for_log.get("accuracy", 10.0)
        grammar = scores_for_log.get("grammar", 10.0)
        relevance = scores_for_log.get("relevance", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(f"AnswerShortQuestion Evaluation: Overall={overall:.2f} (Accuracy: {accuracy:.2f}, Grammar: {grammar:.2f}, Relevance: {relevance:.2f})")
        
        # Add the raw user response to the result for debugging/info
        processed_result["user_response_text"] = user_response

        logger.debug("--- AnswerShortQuestionEvaluator: Finished evaluation ---")
        return processed_result