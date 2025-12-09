# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re

# class ReadAloudEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Preprocessing
#         user_response = user_response.strip()

#         # Word Count Feedback
#         word_count = len(user_response.split())
#         prompt_word_count = len(prompt.split())

#         word_count_feedback = ""
#         if word_count < prompt_word_count * 0.9:
#             word_count_feedback = f"⚠️ Your response is shorter than the original passage ({word_count} vs {prompt_word_count} words). Some parts may be missing."
#         elif word_count > prompt_word_count * 1.1:
#             word_count_feedback = f"⚠️ Your response has extra content or paraphrasing ({word_count} vs {prompt_word_count} words)."
#         else:
#             word_count_feedback = "✅ Response length matches the passage."

#         # Spell Check (basic)
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

#         instruction = f"""
# You are a PTE expert evaluating the "Read Aloud" task.

# Passage: {prompt}
# User Said: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Pronunciation: Clarity and accuracy of speech sounds
# - Intonation: Natural pitch variation and rhythm
# - Stress: Emphasis on correct syllables and words
# - Fluency: Smoothness of expression, minimal hesitation

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "pronunciation": <number>,
#     "intonation": <number>,
#     "stress": <number>,
#     "fluency": <number>
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
#                 "pronunciation": 0.30,
#                 "intonation": 0.20,
#                 "stress": 0.15,
#                 "fluency": 0.25
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

# # src/evaluators/read_aloud_evaluator.py

# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class ReadAloudEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Read Aloud task.
#     Uses an LLM for scoring Pronunciation, Intonation, Stress, and Fluency.
#     Integrates preprocessing for word count and length comparison.
#     """
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- ReadAloudEvaluator: Starting evaluation ---")
        
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         prompt_word_count = len(prompt.split())

#         word_count_feedback = ""
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please read the passage aloud."
#         elif word_count < prompt_word_count * 0.95: 
#             word_count_feedback = f"⚠️ Your response is significantly shorter than the original passage ({word_count} vs {prompt_word_count} words). Some parts may be missing or you stopped early."
#         elif word_count > prompt_word_count * 1.05: 
#             word_count_feedback = f"⚠️ Your response has extra content or paraphrasing ({word_count} vs {prompt_word_count} words). You should read the passage exactly as it is written."
#         else:
#             word_count_feedback = "✅ Response length matches the passage closely."

#         # --- Construct the instruction/prompt for the LLM ---
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Read Aloud" task.
# In this task, the user is expected to read a given passage exactly as it is written, maintaining natural pronunciation, intonation, and rhythm, and speaking fluently without hesitations.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of pronunciation, intonation, and stress will be inferred from the textual representation (e.g., sentence structure, punctuation, word choice) and how well the transcription matches the original passage.

# Passage to be read: {prompt}
# User's Transcription: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count (User): {word_count}
# - Word Count (Passage): {prompt_word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - pronunciation: Based on the transcription's accuracy to the original and the clarity of word forms, how well can we infer correct pronunciation?
# - intonation: Based on the transcription's phrasing and punctuation, does it suggest natural pitch variation and rhythm in speech?
# - stress: Based on the transcription, does the phrasing and word choice suggest appropriate emphasis on correct syllables and words?
# - fluency: How smoothly and naturally does the transcription read, indicating minimal hesitation, repetition, or false starts in the original speech? Also, how well does the transcription match the original passage without omissions or additions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "pronunciation": <number>,
#     "intonation": <number>,
#     "stress": <number>,
#     "fluency": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"ReadAloud LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # The keys here are the *standardized output keys* for our system.
#         # BaseEvaluator will find the corresponding values in LLM's raw output.
#         # Specify llm_output_max_scale for each score if it's NOT 90.
#         score_key_map = {
#             "pronunciation": {"key": "pronunciation", "llm_output_max_scale": 90}, # LLM returning 90, so keep 90
#             "intonation": {"key": "intonation", "llm_output_max_scale": 90}, # LLM returning 85, so keep 90
#             "stress": {"key": "stress", "llm_output_max_scale": 90}, # LLM returning 80, so keep 90
#             "fluency": {"key": "fluency", "llm_output_max_scale": 90} # LLM returning 90, so keep 90
#         }
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": 90} # LLM returning values like 90, so keep 90

#         # --- Call BaseEvaluator for LLM Score ---
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=90, # Default for this evaluator, used if not specified per sub-score
#             default_feedback_message="" # Prevent generic BaseEvaluator feedback
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         # Start with the feedback already processed/aggregated by BaseEvaluator.
#         if processed_result.get("feedback"):
#             final_feedback_parts.append(processed_result["feedback"])
        
#         # Add automated feedback if it's not empty
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
        
#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         scores_for_log = processed_result.get("scores", {})
#         pronunciation = scores_for_log.get("pronunciation", 10.0)
#         intonation = scores_for_log.get("intonation", 10.0)
#         stress = scores_for_log.get("stress", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"ReadAloud Evaluation: Overall={overall:.2f} "
#             f"(Pronunciation: {pronunciation:.2f}, Intonation: {intonation:.2f}, "
#             f"Stress: {stress:.2f}, Fluency: {fluency:.2f})"
#         )

#         return processed_result


# src/evaluators/read_aloud_evaluator.py on 8/10/25

# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class ReadAloudEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Read Aloud task.
#     Uses an LLM for scoring Pronunciation, Intonation, Stress, and Fluency,
#     inferred from the transcription.
#     Integrates preprocessing for word count and length comparison.
#     """
#     def __init__(self):
#         super().__init__()
#         # Define the raw scale the LLM is expected to output for each trait.
#         # Based on the prompt and observed LLM behavior (e.g., 90, 85, 80, 10),
#         # the LLM is attempting to output on a 0-90 scale for all.
#         self.trait_definitions = {
#             "pronunciation": {"llm_output_max_scale": 90},
#             "intonation": {"llm_output_max_scale": 90},
#             "stress": {"llm_output_max_scale": 90},
#             "fluency": {"llm_output_max_scale": 90},
#             "overall_score": {"llm_output_max_scale": 90} # Assuming overall is also 0-90 from LLM
#         }

#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- ReadAloudEvaluator: Starting evaluation ---")
        
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         prompt_word_count = len(re.findall(r'\b\w+\b', prompt)) # More robust word count, ignoring punctuation
        
#         word_count_feedback = ""
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please read the passage aloud."
#         # The prompt_word_count needs to be robust. `prompt.split()` can be inaccurate with punctuation.
#         # `re.findall(r'\b\w+\b', prompt)` is better.
#         # Adjusted percentages slightly for typical variation.
#         elif word_count < prompt_word_count * 0.90: 
#             word_count_feedback = f"⚠️ Your response is significantly shorter than the original passage ({word_count} vs {prompt_word_count} words). Some parts may be missing or you stopped early."
#         elif word_count > prompt_word_count * 1.10: 
#             word_count_feedback = f"⚠️ Your response has extra content or paraphrasing ({word_count} vs {prompt_word_count} words). You should read the passage exactly as it is written."
#         else:
#             word_count_feedback = "✅ Response length matches the passage closely."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt explicitly asks for scores on a 0-90 scale, which matches `self.trait_definitions`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Read Aloud" task.
# In this task, the user is expected to read a given passage exactly as it is written, maintaining natural pronunciation, intonation, and rhythm, and speaking fluently without hesitations.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of pronunciation, intonation, and stress will be inferred from the textual representation (e.g., sentence structure, punctuation, word choice) and how well the transcription matches the original passage.

# Passage to be read: {prompt}
# User's Transcription: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count (User): {word_count}
# - Word Count (Passage): {prompt_word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - pronunciation: Based on the transcription's accuracy to the original and the clarity of word forms, how well can we infer correct pronunciation?
# - intonation: Based on the transcription's phrasing and punctuation, does it suggest natural pitch variation and rhythm in speech?
# - stress: Based on the transcription, does the phrasing and word choice suggest appropriate emphasis on correct syllables and words?
# - fluency: How smoothly and naturally does the transcription read, indicating minimal hesitation, repetition, or false starts in the original speech? Also, how well does the transcription match the original passage without omissions or additions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "pronunciation": <number>,
#     "intonation": <number>,
#     "stress": <number>,
#     "fluency": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"ReadAloud LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # Explicitly use llm_output_max_scale from trait_definitions for consistency.
#         score_key_map = {
#             "pronunciation": {"key": "scores.pronunciation", "llm_output_max_scale": self.trait_definitions['pronunciation']['llm_output_max_scale']},
#             "intonation": {"key": "scores.intonation", "llm_output_max_scale": self.trait_definitions['intonation']['llm_output_max_scale']},
#             "stress": {"key": "scores.stress", "llm_output_max_scale": self.trait_definitions['stress']['llm_output_max_scale']},
#             "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']}
#         }
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

#         # --- Call BaseEvaluator for LLM Score ---
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=90, # Fallback default if any key is missing or not in map
#             default_feedback_message="" # Prevent generic BaseEvaluator feedback if LLM provides none
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         # Start with the feedback already processed/aggregated by BaseEvaluator.
#         if processed_result.get("feedback"):
#             final_feedback_parts.append(processed_result["feedback"])
        
#         # Add automated feedback if it's not empty
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
        
#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         scores_for_log = processed_result.get("scores", {})
#         pronunciation = scores_for_log.get("pronunciation", 10.0)
#         intonation = scores_for_log.get("intonation", 10.0)
#         stress = scores_for_log.get("stress", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"ReadAloud Evaluation: Overall={overall:.2f} "
#             f"(Pronunciation: {pronunciation:.2f}, Intonation: {intonation:.2f}, "
#             f"Stress: {stress:.2f}, Fluency: {fluency:.2f})"
#         )

#         return processed_result


# src/evaluators/read_aloud_evaluator.py

from evaluators.base_evaluator import BaseEvaluator
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReadAloudEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Read Aloud task.
    Uses an LLM for scoring Pronunciation, Intonation, Stress, and Fluency,
    inferred from the transcription.
    Integrates preprocessing for word count and length comparison.
    """
    def __init__(self):
        super().__init__()
        # Define the raw scale the LLM is expected to output for each trait.
        self.trait_definitions = {
            "pronunciation": {"llm_output_max_scale": 90},
            "intonation": {"llm_output_max_scale": 90},
            "stress": {"llm_output_max_scale": 90},
            "fluency": {"llm_output_max_scale": 90}, # Ensure fluency is defined
            "overall_score": {"llm_output_max_scale": 90}
        }

    def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
        logger.debug("--- ReadAloudEvaluator: Starting evaluation ---")
        
        user_response = user_response.strip()

        # --- Automated Preprocessing and Feedback Generation ---
        word_count = len(user_response.split())
        prompt_word_count = len(re.findall(r'\b\w+\b', prompt))
        
        word_count_feedback = ""
        if word_count == 0:
            word_count_feedback = "⚠️ Your response is empty. Please read the passage aloud."
        elif word_count < prompt_word_count * 0.90: 
            word_count_feedback = f"⚠️ Your response is significantly shorter than the original passage ({word_count} vs {prompt_word_count} words). Some parts may be missing or you stopped early."
        elif word_count > prompt_word_count * 1.10: 
            word_count_feedback = f"⚠️ Your response has extra content or paraphrasing ({word_count} vs {prompt_word_count} words). You should read the passage exactly as it is written."
        else:
            word_count_feedback = "✅ Response length matches the passage closely."

        # --- Construct the instruction/prompt for the LLM ---
        # [FIX]: Make the JSON output format strictly adhere to the "scores" nesting
        # and explicitly include "fluency" with a score.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Read Aloud" task.
In this task, the user is expected to read a given passage exactly as it is written, maintaining natural pronunciation, intonation, and rhythm, and speaking fluently without hesitations.

IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
Therefore, your assessment of pronunciation, intonation, and stress will be inferred from the textual representation (e.g., sentence structure, punctuation, word choice) and how well the transcription matches the original passage.

Passage to be read: {prompt}
User's Transcription: {user_response}

Additional Info for your consideration:
- {word_count_feedback}
- Word Count (User): {word_count}
- Word Count (Passage): {prompt_word_count}

Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
- pronunciation: Based on the transcription's accuracy to the original and the clarity of word forms, how well can we infer correct pronunciation?
- intonation: Based on the transcription's phrasing and punctuation, does it suggest natural pitch variation and rhythm in speech?
- stress: Based on the transcription, does the phrasing and word choice suggest appropriate emphasis on correct syllables and words?
- fluency: How smoothly and naturally does the transcription read, indicating minimal hesitation, repetition, or false starts in the original speech? Also, how well does the transcription match the original passage without omissions or additions?

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

Format your output EXACTLY LIKE THIS JSON. Ensure all scores are integers between 0 and 90.
{{
  "scores": {{
    "pronunciation": <number>,
    "intonation": <number>,
    "stress": <number>,
    "fluency": <number>
  }},
  "overall_score": <number>,
  "feedback": "<string>"
}}
"""
        logger.debug(f"ReadAloud LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

        # --- Define score key mapping ---
        # [FIX]: Update score_key_map to point to the nested "scores" object.
        score_key_map = {
            "pronunciation": {"key": "scores.pronunciation", "llm_output_max_scale": self.trait_definitions['pronunciation']['llm_output_max_scale']},
            "intonation": {"key": "scores.intonation", "llm_output_max_scale": self.trait_definitions['intonation']['llm_output_max_scale']},
            "stress": {"key": "scores.stress", "llm_output_max_scale": self.trait_definitions['stress']['llm_output_max_scale']},
            "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=90,
            default_feedback_message=""
        )
        
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        if word_count_feedback.strip():
            final_feedback_parts.append(word_count_feedback)
        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        scores_for_log = processed_result.get("scores", {})
        pronunciation = scores_for_log.get("pronunciation", 10.0)
        intonation = scores_for_log.get("intonation", 10.0)
        stress = scores_for_log.get("stress", 10.0)
        fluency = scores_for_log.get("fluency", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(
            f"ReadAloud Evaluation: Overall={overall:.2f} "
            f"(Pronunciation: {pronunciation:.2f}, Intonation: {intonation:.2f}, "
            f"Stress: {stress:.2f}, Fluency: {fluency:.2f})"
        )

        return processed_result