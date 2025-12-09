# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking

# class WriteEmailEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Aim for at least 50 words."
#         elif word_count > 150:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it under 150 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate."

#         # Spell check
#         try:
#             blob = TextBlob(user_response)
#             misspelled_words = [word for word in blob.words if word != TextBlob(word).correct()]
#             spell_check_feedback = "Spelling is mostly correct." if not misspelled_words else f"🟥 Found possible spelling issues: {', '.join(misspelled_words)}"
#         except Exception as e:
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         instruction = f"""
# You are a PTE expert evaluating the "Write Email" task.

# Prompt: {prompt}
# User Response: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Task Achievement: Did the response fully address the email prompt?
# - Coherence: Is the information logically organized?
# - Fluency: Smoothness of expression, minimal awkward phrasing
# - Grammar: Sentence variety and accuracy
# - Vocabulary: Range and precision of word usage

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "coherence": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """

#         result = self._get_openai_score(instruction)

#         # Apply weighted average
#         if "scores" in result:
#             scores = result["scores"]
#             weights = {
#                 "task_achievement": 0.25,
#                 "coherence": 0.25,
#                 "fluency": 0.20,
#                 "grammar": 0.15,
#                 "vocabulary": 0.15
#             }

#             overall = sum(scores[k] * weights.get(k, 0) for k in scores if k in weights)
#             result["overall_score"] = round(overall, 1)

#         # Append pre-processing feedback
#         additional_feedback = []
#         if "feedback" in result:
#             # Ensure feedback is a string
#             feedback = result["feedback"]
#             if isinstance(feedback, dict):
#                 feedback = str(feedback)  # Convert dict to string if necessary
#             additional_feedback.append(feedback)
#         additional_feedback.append(word_count_feedback)
#         additional_feedback.append(spell_check_feedback)

#         result["feedback"] = "\n".join(additional_feedback)

#         return result
    

#     #################### ok ########################

# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking
# import re
# import logging
# from typing import Dict, Any, Union

# logger = logging.getLogger(__name__)

# class WriteEmailEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- WriteEmailEvaluator: Starting evaluation ---")

#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Write Email: 50-150 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your email is empty. Please write an email."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Write Email', aim for 50–150 words to fully address the prompt."
#         elif word_count > 150:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 150 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (50-150 words)."

#         # Spell check (relevant for writing task)
#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Make spell check case-insensitive and get unique misspelled words
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word.lower()).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in WriteEmailEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # IMPORTANT: While the prompt ASKS for 0-90, we assume the LLM *returned* 0-10 in initial tests.
#         # We will keep the prompt asking for 0-90, but tell the BaseEvaluator
#         # that the LLM's *actual* output range is 0-10 for robust scaling.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Write Email" task.
# The user must write an email responding to a given prompt, ensuring appropriate tone, clear communication, and adherence to email conventions.

# Prompt: {prompt}
# User's Email: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Task Achievement: Did the email fully address all aspects of the prompt, including purpose, audience, and required information?
# - Coherence: Is the email logically organized with clear paragraphs, smooth transitions, and a clear overall message?
# - Fluency: (Interpreted as textual flow and natural phrasing for a written response) Is the writing smooth, easy to read, and free from awkward phrasing or unnatural sentence structures?
# - Grammar: Are sentence structures accurate, varied, and appropriate for an email, demonstrating good control of grammar?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for the context and tone of the email?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "coherence": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"WriteEmail LLM Prompt: {instruction[:self.max_input_length]}")

#         # --- Call BaseEvaluator for LLM Score ---
#         score_key_map = {
#             "task_achievement": {"key": "scores.task_achievement"},
#             "coherence": {"key": "scores.coherence"},
#             "fluency": {"key": "scores.fluency"},
#             "grammar": {"key": "scores.grammar"},
#             "vocabulary": {"key": "scores.vocabulary"}
#         }
#         overall_score_key = "overall_score"

#         # FIX: Tell BaseEvaluator that the LLM ACTUALLY returns 0-10 scores (if that was the case initially),
#         # and explicitly prevent generic feedback from BaseEvaluator.
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10, # <-- CRITICAL FIX HERE (assuming initial output was 0-10)
#             default_feedback_message="" # <-- CRITICAL FIX HERE: Prevent generic BaseEvaluator feedback
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         llm_output_feedback = processed_result.get("feedback", "").strip()

#         # FIX: Check if the feedback from the LLM (or BaseEvaluator's aggregation) is empty or generic
#         if not llm_output_feedback or llm_output_feedback == "No specific feedback from LLM.":
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this email.") # <-- IMPROVED DEFAULT
#         elif llm_output_feedback: # If it's not empty and not the generic string
#             final_feedback_parts.append(llm_output_feedback)
        
#         # Add automated feedback after LLM's comments
#         final_feedback_parts.append(word_count_feedback)
#         final_feedback_parts.append(spell_check_feedback)

#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are already guaranteed to be floats within 10.0-90.0 range due to BaseEvaluator scaling.
#         scores_for_log = processed_result.get("scores", {})
#         task_achievement = scores_for_log.get("task_achievement", 10.0)
#         coherence = scores_for_log.get("coherence", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"WriteEmail Evaluation: Overall={overall:.2f} "
#             f"(Task Achievement: {task_achievement:.2f}, Coherence: {coherence:.2f}, "
#             f"Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f})"
#         )

#         return processed_result


# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking
# import re
# import logging
# from typing import Dict, Any, Union

# logger = logging.getLogger(__name__)

# class WriteEmailEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Write Email task.
#     Uses an LLM for scoring Task Achievement, Coherence, Fluency, Grammar, and Vocabulary.
#     Integrates preprocessing for word count and spell check.
#     """
#     def __init__(self):
#         super().__init__()
#         # Define the raw scale the LLM is expected to output for each trait.
#         # Based on your assumption, the LLM outputs 0-10, which BaseEvaluator then scales.
#         self.trait_definitions = {
#             "task_achievement": {"llm_output_max_scale": 10},
#             "coherence": {"llm_output_max_scale": 10},
#             "fluency": {"llm_output_max_scale": 10},
#             "grammar": {"llm_output_max_scale": 10},
#             "vocabulary": {"llm_output_max_scale": 10},
#             "overall_score": {"llm_output_max_scale": 10} # Assuming overall is also 0-10 from LLM
#         }

#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- WriteEmailEvaluator: Starting evaluation ---")

#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Write Email: 50-150 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your email is empty. Please write an email."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Write Email', aim for 50–150 words to fully address the prompt."
#         elif word_count > 150:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 150 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (50-150 words)."

#         # Spell check (relevant for writing task)
#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Make spell check case-insensitive and get unique misspelled words
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word.lower()).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in WriteEmailEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [CRITICAL FIX]: Change the LLM prompt to ask for scores on a 0-10 scale
#         # to match the LLM's *actual* expected output and `llm_output_max_scale`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Write Email" task.
# The user must write an email responding to a given prompt, ensuring appropriate tone, clear communication, and adherence to email conventions.

# Prompt: {prompt}
# User's Email: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
# - Task Achievement: Did the email fully address all aspects of the prompt, including purpose, audience, and required information?
# - Coherence: Is the email logically organized with clear paragraphs, smooth transitions, and a clear overall message?
# - Fluency: (Interpreted as textual flow and natural phrasing for a written response) Is the writing smooth, easy to read, and free from awkward phrasing or unnatural sentence structures?
# - Grammar: Are sentence structures accurate, varied, and appropriate for an email, demonstrating good control of grammar?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for the context and tone of the email?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 10.
# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "coherence": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"WriteEmail LLM Prompt: {instruction[:self.max_input_length]}")

#         # --- Call BaseEvaluator for LLM Score ---
#         # Explicitly use llm_output_max_scale from trait_definitions for consistency.
#         score_key_map = {
#             "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
#             "coherence": {"key": "scores.coherence", "llm_output_max_scale": self.trait_definitions['coherence']['llm_output_max_scale']},
#             "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
#             "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
#             "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']}
#         }
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10, # Fallback default if any key is missing or not in map
#             default_feedback_message="" # Prevent generic BaseEvaluator feedback
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         llm_output_feedback = processed_result.get("feedback", "").strip()

#         # [FIX]: Refined feedback aggregation to ensure a specific message if LLM/BaseEvaluator returns nothing useful.
#         if not llm_output_feedback:
#             # If BaseEvaluator's aggregation resulted in empty feedback, provide a task-specific default
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this email. Ensure your email addresses all aspects of the prompt clearly and concisely.")
#         else:
#             final_feedback_parts.append(llm_output_feedback)
        
#         # Add automated feedback after LLM's comments
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
#         if spell_check_feedback.strip():
#             final_feedback_parts.append(spell_check_feedback)

#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are already guaranteed to be floats within 10.0-90.0 range due to BaseEvaluator scaling.
#         scores_for_log = processed_result.get("scores", {})
#         task_achievement = scores_for_log.get("task_achievement", 10.0)
#         coherence = scores_for_log.get("coherence", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"WriteEmail Evaluation: Overall={overall:.2f} "
#             f"(Task Achievement: {task_achievement:.2f}, Coherence: {coherence:.2f}, "
#             f"Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f})"
#         )

#         return processed_result


from evaluators.base_evaluator import BaseEvaluator
from textblob import TextBlob  # For basic spell checking
import re
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

class WriteEmailEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Write Email task.
    Uses an LLM for scoring Task Achievement, Coherence, Fluency, Grammar, and Vocabulary.
    Integrates preprocessing for word count and spell check.
    """
    def __init__(self):
        super().__init__()
        # Define the raw scale the LLM is expected to output for each trait (0-10).
        self.trait_definitions = {
            "task_achievement": {"llm_output_max_scale": 10},
            "coherence": {"llm_output_max_scale": 10},
            "fluency": {"llm_output_max_scale": 10},
            "grammar": {"llm_output_max_scale": 10},
            "vocabulary": {"llm_output_max_scale": 10},
            "overall_score": {"llm_output_max_scale": 10} # Assuming overall is also 0-10 from LLM
        }

    def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
        logger.debug("--- WriteEmailEvaluator: Starting evaluation ---")

        # Preprocessing
        user_response = user_response.strip()

        # --- Automated Preprocessing and Feedback Generation ---
        # Word count feedback
        word_count = len(user_response.split())
        word_count_feedback = ""

        # PTE guidance for Write Email: 50-150 words.
        if word_count == 0:
            word_count_feedback = "⚠️ Your email is empty. Please write an email."
        elif word_count < 50:
            word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Write Email', aim for 50–150 words to fully address the prompt."
        elif word_count > 150:
            word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 150 words."
        else:
            word_count_feedback = "✅ Word count is appropriate (50-150 words)."

        # Spell check (relevant for writing task)
        spell_check_feedback = ""
        try:
            blob = TextBlob(user_response)
            misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word.lower()).correct()).lower()]
            if misspelled_words:
                spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
            else:
                spell_check_feedback = "✅ Spelling appears correct."
        except Exception as e:
            logger.error(f"Error during spell check in WriteEmailEvaluator: {e}", exc_info=True)
            spell_check_feedback = "Spell check skipped due to technical issue."

        # --- Construct the instruction/prompt for the LLM ---
        # [MODIFIED]: Removed the explicit JSON format example from the user prompt.
        # BaseEvaluator will now inject a strict JSON schema into the system message.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Write Email" task.
The user must write an email responding to a given prompt, ensuring appropriate tone, clear communication, and adherence to email conventions.

Prompt: {prompt}
User's Email: {user_response}

Additional Info for your consideration:
- {word_count_feedback}
- {spell_check_feedback}
- Word Count: {word_count}

Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
- task_achievement: Did the email fully address all aspects of the prompt, including purpose, audience, and required information?
- coherence: Is the email logically organized with clear paragraphs, smooth transitions, and a clear overall message?
- fluency: (Interpreted as textual flow and natural phrasing for a written response) Is the writing smooth, easy to read, and free from awkward phrasing or unnatural sentence structures?
- grammar: Are sentence structures accurate, varied, and appropriate for an email, demonstrating good control of grammar?
- vocabulary: Is the vocabulary varied, precise, and appropriate for the context and tone of the email?

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"WriteEmail LLM Prompt: {instruction[:self.max_input_length]}")

        # --- Call BaseEvaluator for LLM Score ---
        score_key_map = {
            "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
            "coherence": {"key": "scores.coherence", "llm_output_max_scale": self.trait_definitions['coherence']['llm_output_max_scale']},
            "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
            "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
            "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=10, # Fallback default if any key is missing or not in map
            default_feedback_message="" # Prevent generic BaseEvaluator feedback if LLM provides none
        )
        
        # --- Combine LLM Feedback with Automated Feedback ---
        final_feedback_parts = []
        
        llm_output_feedback = processed_result.get("feedback", "").strip()

        if not llm_output_feedback:
            final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this email. Ensure your email addresses all aspects of the prompt clearly and concisely.")
        else:
            final_feedback_parts.append(llm_output_feedback)
        
        if word_count_feedback.strip():
            final_feedback_parts.append(word_count_feedback)
        if spell_check_feedback.strip():
            final_feedback_parts.append(spell_check_feedback)

        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        # --- Logging Final Scores (Crucial for debugging and verification) ---
        scores_for_log = processed_result.get("scores", {})
        task_achievement = scores_for_log.get("task_achievement", 10.0)
        coherence = scores_for_log.get("coherence", 10.0)
        fluency = scores_for_log.get("fluency", 10.0)
        grammar = scores_for_log.get("grammar", 10.0)
        vocabulary = scores_for_log.get("vocabulary", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(
            f"WriteEmail Evaluation: Overall={overall:.2f} "
            f"(Task Achievement: {task_achievement:.2f}, Coherence: {coherence:.2f}, "
            f"Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f})"
        )

        return processed_result