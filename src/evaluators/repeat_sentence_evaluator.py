# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re

# class RepeatSentenceEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Preprocessing
#         user_response = user_response.strip()

#         # Word Count
#         word_count = len(user_response.split())
#         prompt_word_count = len(prompt.split())

#         word_count_feedback = ""
#         if word_count < prompt_word_count - 2:
#             word_count_feedback = f"⚠️ Your response is shorter than the original sentence. Some words may be missing."
#         elif word_count > prompt_word_count + 2:
#             word_count_feedback = f"⚠️ Your response has extra words or is longer than the original sentence."
#         else:
#             word_count_feedback = "✅ Response length matches the original sentence."

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

#         instruction = f"""
# You are a PTE expert evaluating the "Repeat Sentence" task.

# Prompt: {prompt}
# User Said: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Accuracy: How closely did the user repeat the sentence?
# - Intonation: Was the tone natural and appropriate?
# - Stress: Were key syllables/words emphasized correctly?
# - Fluency: Was speech smooth and uninterrupted?

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "accuracy": <number>,
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
#                 "accuracy": 0.40,
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




# # src/evaluators/repeat_sentence_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class RepeatSentenceEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Repeat Sentence task.
#     Uses an LLM for scoring Accuracy, Intonation, Stress, and Fluency,
#     inferred from the transcription.
#     Integrates preprocessing for word count and length comparison.
#     """
#     def __init__(self):
#         super().__init__()
#         # Define the raw scale the LLM is expected to output for each trait.
#         # The prompt asks for 0-90, and LLMs usually try to follow this.
#         self.trait_definitions = {
#             "accuracy": {"llm_output_max_scale": 90},
#             "intonation": {"llm_output_max_scale": 90},
#             "stress": {"llm_output_max_scale": 90},
#             "fluency": {"llm_output_max_scale": 90},
#             "overall_score": {"llm_output_max_scale": 90} # Assuming overall is also 0-90 from LLM
#         }

#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- RepeatSentenceEvaluator: Starting evaluation ---")
        
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         # [FIX]: Use regex for more robust word count from prompt, similar to ReadAloud
#         prompt_word_count = len(re.findall(r'\b\w+\b', prompt))

#         word_count_feedback = ""
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please repeat the sentence."
#         # Allow for a small deviation in word count due to transcription nuances
#         # Adjusted percentages slightly to be consistent with ReadAloud
#         elif word_count < prompt_word_count * 0.90: 
#             word_count_feedback = f"⚠️ Your response is significantly shorter than the original sentence ({word_count} vs {prompt_word_count} words). Some words may be missing, affecting content accuracy."
#         elif word_count > prompt_word_count * 1.10: 
#             word_count_feedback = f"⚠️ Your response has extra words or is longer than the original sentence ({word_count} vs {prompt_word_count} words). You should repeat the sentence exactly."
#         else:
#             word_count_feedback = "✅ Response length matches the original sentence closely."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt requests a nested structure for granular comments.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Repeat Sentence" task.
# In this task, the user must repeat a sentence exactly as heard, maintaining the original meaning, pronunciation, intonation, and rhythm.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of intonation, stress, and fluency will be inferred from the textual representation (e.g., sentence structure, punctuation, word choice) and how accurately the transcription matches the original sentence.

# Original Sentence: {prompt}
# User's Transcription: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count (User): {word_count}
# - Word Count (Original): {prompt_word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Accuracy: How closely does the user's transcription match the original sentence, both in content and word order? (This is the most critical aspect for Repeat Sentence).
# - Intonation: Based on the transcription's phrasing and punctuation, does it suggest natural pitch variation and rhythm in speech?
# - Stress: Based on the transcription, does the phrasing and word choice suggest appropriate emphasis on correct syllables and words?
# - Fluency: How smoothly and naturally does the transcription read, indicating minimal hesitation, repetition, or false starts in the original speech? Also, how well does the transcription match the original sentence without omissions or additions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "evaluation": {{
#     "accuracy": {{"score": <number>, "comments": "<string>"}},
#     "intonation": {{"score": <number>, "comments": "<string>"}},
#     "stress": {{"score": <number>, "comments": "<string>"}},
#     "fluency": {{"score": <number>, "comments": "<string>"}}
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"RepeatSentence LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Call BaseEvaluator for LLM Score ---
#         # Explicitly use llm_output_max_scale from trait_definitions for consistency.
#         score_key_map = {
#             "accuracy": {"key": "evaluation.accuracy.score", "llm_output_max_scale": self.trait_definitions['accuracy']['llm_output_max_scale']},
#             "intonation": {"key": "evaluation.intonation.score", "llm_output_max_scale": self.trait_definitions['intonation']['llm_output_max_scale']},
#             "stress": {"key": "evaluation.stress.score", "llm_output_max_scale": self.trait_definitions['stress']['llm_output_max_scale']},
#             "fluency": {"key": "evaluation.fluency.score", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']}
#         }
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=90, # Fallback default if any key is missing or not in map
#             default_feedback_message="" # Prevent generic BaseEvaluator feedback if LLM provides none
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         llm_output_feedback = processed_result.get("feedback", "").strip()

#         # [FIX]: Refined feedback aggregation to ensure a specific message if LLM/BaseEvaluator returns nothing useful.
#         if not llm_output_feedback:
#             # If BaseEvaluator's aggregation resulted in empty feedback, provide a task-specific default
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this response. Ensure your response is accurate, clear, and matches the original sentence closely.")
#         else:
#             final_feedback_parts.append(llm_output_feedback)
        
#         # Add automated feedback after LLM's comments
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
        
#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         scores_for_log = processed_result.get("scores", {})
#         accuracy = scores_for_log.get("accuracy", 10.0)
#         intonation = scores_for_log.get("intonation", 10.0)
#         stress = scores_for_log.get("stress", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"RepeatSentence Evaluation: Overall={overall:.2f} "
#             f"(Accuracy: {accuracy:.2f}, Intonation: {intonation:.2f}, "
#             f"Stress: {stress:.2f}, Fluency: {fluency:.2f})"
#         )

#         return processed_result


# src/evaluators/repeat_sentence_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
import logging
import re # Assuming you might use regex for advanced checks

logger = logging.getLogger(__name__)

class RepeatSentenceEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Repeat Sentence task.
    Uses an LLM for scoring Content, Fluency, and Pronunciation.
    """
    def __init__(self):
        super().__init__()
        self.trait_definitions = {
            "content": {"llm_output_max_scale": 90},
            "fluency": {"llm_output_max_scale": 90},
            "pronunciation": {"llm_output_max_scale": 90},
            "overall_score": {"llm_output_max_scale": 90}
        }

    def evaluate(self, prompt: str, user_response: str) -> dict:
        logger.debug("--- RepeatSentenceEvaluator: Starting evaluation ---")
        user_response = user_response.strip()

        # --- Automated Feedback Generation ---
        # Basic check for response length against original sentence
        original_sentence_len = len(prompt.split())
        user_response_len = len(user_response.split())
        
        length_feedback = ""
        if user_response_len == 0:
            length_feedback = "⚠️ Your response is empty. You must repeat the sentence."
        elif abs(original_sentence_len - user_response_len) > max(1, original_sentence_len * 0.2): # Allow for 20% deviation or 1 word
            length_feedback = f"⚠️ Your response length ({user_response_len} words) deviates significantly from the original ({original_sentence_len} words). Focus on repeating accurately."
        else:
            length_feedback = "✅ Response length matches the original sentence closely."

        # --- LLM Instruction (Prompt) Preparation ---
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Repeat Sentence" task.
The user's goal is to repeat the given sentence *exactly* as they heard it, maintaining natural fluency and clear pronunciation.

Original Sentence: {prompt}
User Repeated: {user_response}

Additional Info for your consideration (these are observations, not scores from you directly):
- {length_feedback}

Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
- Content: How much of the original sentence did the user repeat correctly? Were words omitted, added, or substituted? (0-90)
- Fluency: How natural and smooth was the user's speech? Was there appropriate pacing, rhythm, and intonation? Were there hesitations, repetitions, or false starts? (0-90)
- Pronunciation: How accurately did the user pronounce words? Are sounds clear? Are there any mispronunciations? (0-90)

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"RepeatSentence LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

        # --- Call BaseEvaluator for LLM Score ---
        score_key_map = {
            "content": {"key": "scores.content", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']},
            "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
            "pronunciation": {"key": "scores.pronunciation", "llm_output_max_scale": self.trait_definitions['pronunciation']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=90,
            default_feedback_message="The AI model could not process your answer for Repeat Sentence due to an internal error or connection issue. Please try again." # More specific default feedback
        )

        # --- Combine LLM Feedback with Automated Feedback ---
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        
        if processed_result.get("overall_score", 0) > 10.0 or not processed_result.get("feedback"):
             final_feedback_parts.append(length_feedback)

        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        # --- Logging Final Scores ---
        scores_for_log = processed_result.get("scores", {})
        content = scores_for_log.get("content", 10.0)
        fluency = scores_for_log.get("fluency", 10.0)
        pronunciation = scores_for_log.get("pronunciation", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(f"RepeatSentence Evaluation: Overall={overall:.2f} (Content: {content:.2f}, Fluency: {fluency:.2f}, Pronunciation: {pronunciation:.2f})")
        
        processed_result["user_response_text"] = user_response

        logger.debug("--- RepeatSentenceEvaluator: Finished evaluation ---")
        return processed_result