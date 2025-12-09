# # summarize_written_text_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spelling check
# import re

# class SummarizeWrittenTextEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count < 5:
#             word_count_feedback = f"⚠️ Summary is too short ({word_count} words). Try to write at least 5 words."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Summary is too long ({word_count} words). Keep it under 75 words."
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
# You are a PTE expert evaluating the "Summarize Written Text" task, aligning with official PTE Academic and Core scoring criteria.

# Passage: {prompt}
# Summary Provided: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Evaluate the summary based on the following PTE scoring criteria:
# - Content (0–5): Does it cover all main ideas of the passage accurately and concisely?
# - Form (0–5): Is it a single, well-formed sentence within 5–75 words?
# - Grammar (0–5): Accuracy and variety of grammatical structures.
# - Vocabulary (0–5): Relevance, precision, and range of vocabulary.
# - Spelling and Punctuation (0–5): Accuracy of spelling and punctuation.

# Map scores to PTE scale (0–90):
# - 5: 85–90 (excellent)
# - 4: 70–84 (good)
# - 3: 55–69 (satisfactory)
# - 2: 40–54 (limited)
# - 1: 25–39 (poor)
# - 0: 0–24 (inadequate)

# Respond in the following JSON format:

# {{
#   "scores": {{
#     "content_coverage": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "sentence_structure": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """

#         result = self._get_openai_score(instruction)

#         # Validate scores against feedback
#         if "scores" in result and "feedback" in result:
#             feedback = result["feedback"].lower()
#             # Check for positive feedback keywords
#             positive_indicators = ["excellent", "perfect", "flawless", "outstanding", "impeccable", "top-tier"]
#             is_positive = any(indicator in feedback for indicator in positive_indicators)
#             scores = result["scores"]
#             # If feedback is positive but any score is anomalously low (e.g., <=50), override with high scores
#             if is_positive and any(score <= 50 for score in scores.values()):
#                 scores = {
#                     "content_coverage": 85,
#                     "grammar": 85,
#                     "vocabulary": 85,
#                     "sentence_structure": 85,
#                     "spelling_punctuation": 85
#                 }
#                 result["scores"] = scores
#                 result["feedback"] += "\nNote: Scores adjusted due to discrepancy between positive feedback and low scores."
#             # Ensure overall_score reflects individual scores
#             weights = {
#                 "content_coverage": 0.30,
#                 "grammar": 0.25,
#                 "vocabulary": 0.20,
#                 "sentence_structure": 0.15,
#                 "spelling_punctuation": 0.10
#             }
#             overall = sum(scores[k] * weights.get(k, 0) for k in scores if k in weights)
#             result["overall_score"] = round(overall, 1)

#         # Append pre-processing feedback
#         additional_feedback = []
#         if "feedback" in result:
#             additional_feedback.append(result["feedback"])
#         additional_feedback.append(word_count_feedback)
#         additional_feedback.append(spell_check_feedback)

#         result["feedback"] = "\n".join(additional_feedback)

#         return result
    
#     ########## ok ##############
# # src/evaluators/summarize_written_text_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class SummarizeWrittenTextEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Summarize Written Text task.
#     Uses an LLM for scoring Content, Form, Grammar, Vocabulary, and Spelling & Punctuation.
#     """
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         # Preprocessing
#         user_response = user_response.strip()

#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count == 0:
#             word_count_feedback = "⚠️ Your summary is empty. Please provide a summary."
#         elif word_count < 5:
#             word_count_feedback = f"⚠️ Summary is too short ({word_count} words). For 'Summarize Written Text', your summary must be a single sentence between 5–75 words."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Summary is too long ({word_count} words). Your summary must be a single sentence between 5–75 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (5-75 words)."

#         # Spell check (relevant for writing task)
#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Make spell check case-insensitive and get unique misspelled words
#             misspelled_words = [word for word in blob.words if word.lower() != TextBlob(word.lower()).correct().lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(set(misspelled_words))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in SummarizeWrittenTextEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt requests the desired output format directly.
#         # IMPORTANT: While the prompt ASKS for 0-90, your LLM *returned* 0-10 in the sample.
#         # We will keep the prompt asking for 0-90, but tell the BaseEvaluator
#         # that the LLM's *actual* output range is 0-10 for robust scaling.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Summarize Written Text" task.
# The user must summarize a given passage in a single sentence, between 5 and 75 words, capturing all the main ideas.

# Passage to summarize:
# {prompt}

# User's Summary:
# {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Content: Does the summary accurately identify and cover all the main ideas of the passage, without including irrelevant details?
# - Form: Is the summary a single, grammatically correct sentence? (Word count is handled separately, but sentence structure is key here).
# - Grammar: Are the grammatical structures accurate, varied, and complex enough for an academic summary?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for summarizing the passage, including academic terms where relevant?
# - Spelling_Punctuation: Are there any spelling errors or punctuation mistakes?

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "content": <number>,
#     "form": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"SummarizeWrittenText LLM Prompt: {instruction}")

#         # --- Define score key mapping ---
#         score_key_map = {
#             "content": {"key": "scores.content"},
#             "form": {"key": "scores.form"},
#             "grammar": {"key": "scores.grammar"},
#             "vocabulary": {"key": "scores.vocabulary"},
#             "spelling_punctuation": {"key": "scores.spelling_punctuation"}
#         }
#         overall_score_key = "overall_score"

#         # --- Call BaseEvaluator for LLM Score ---
#         # FIX: Tell BaseEvaluator that the LLM ACTUALLY returns 0-10 scores,
#         # despite us asking for 0-90 in the prompt. BaseEvaluator will then scale this to 0-90.
#         # FIX: Pass default_feedback_message="" to _get_openai_score to prevent it from returning "No specific feedback from LLM."
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10, # <-- CRITICAL FIX HERE
#             default_feedback_message="" # <-- CRITICAL FIX HERE
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         llm_output_feedback = processed_result.get("feedback", "").strip()

#         # FIX: Check if the feedback from the LLM (or BaseEvaluator's aggregation) is empty or generic
#         if not llm_output_feedback or llm_output_feedback == "No specific feedback from LLM.":
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this response.") # <-- IMPROVED DEFAULT
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
#         content = scores_for_log.get("content", 10.0)
#         form = scores_for_log.get("form", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"SummarizeWrittenText Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Form: {form:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Spelling/Punctuation: {spelling_punctuation:.2f})"
#         )

#         return processed_result


# # src/evaluators/summarize_written_text_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class SummarizeWrittenTextEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Summarize Written Text task.
#     Uses an LLM for scoring Content, Form, Grammar, Vocabulary, and Spelling & Punctuation.
#     """
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- SummarizeWrittenTextEvaluator: Starting evaluation ---")

#         # Preprocessing
#         user_response = user_response.strip()

#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count == 0:
#             word_count_feedback = "⚠️ Your summary is empty. Please provide a summary."
#         elif word_count < 5:
#             word_count_feedback = f"⚠️ Summary is too short ({word_count} words). For 'Summarize Written Text', your summary must be a single sentence between 5–75 words."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Summary is too long ({word_count} words). Your summary must be a single sentence between 5–75 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (5-75 words)."

#         # Spell check (relevant for writing task)
#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Make spell check case-insensitive and get unique misspelled words
#             misspelled_words = [word for word in blob.words if word.lower() != TextBlob(word.lower()).correct().lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(set(misspelled_words))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in SummarizeWrittenTextEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt requests the desired output format directly.
#         # IMPORTANT: While the prompt ASKS for 0-90, your LLM *returned* 0-10 in the sample.
#         # We will keep the prompt asking for 0-90, but tell the BaseEvaluator
#         # that the LLM's *actual* output range is 0-10 for robust scaling.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Summarize Written Text" task.
# The user must summarize a given passage in a single sentence, between 5 and 75 words, capturing all the main ideas.

# Passage to summarize:
# {prompt}

# User's Summary:
# {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Content: Does the summary accurately identify and cover all the main ideas of the passage, without including irrelevant details?
# - Form: Is the summary a single, grammatically correct sentence? (Word count is handled separately, but sentence structure is key here).
# - Grammar: Are the grammatical structures accurate, varied, and complex enough for an academic summary?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for summarizing the passage, including academic terms where relevant?
# - Spelling_Punctuation: Are there any spelling errors or punctuation mistakes?

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "content": <number>,
#     "form": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"SummarizeWrittenText LLM Prompt: {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # These keys directly correspond to the expected structure in normalized_llm_output["scores"]
#         score_key_map = {
#             "content": {"key": "content"}, # Simple key expected in normalized_llm_output["scores"]
#             "form": {"key": "form"},
#             "grammar": {"key": "grammar"},
#             "vocabulary": {"key": "vocabulary"},
#             "spelling_punctuation": {"key": "spelling_punctuation"}
#         }
#         overall_score_key = "overall_score" # Simple key for overall_score in normalized_llm_output

#         # --- Call BaseEvaluator for LLM Score ---
#         # Pass an empty string as default_feedback_message to BaseEvaluator,
#         # so it doesn't add its generic fallback if the LLM provides nothing.
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10, # LLM output was 0-10, BaseEvaluator scales to 0-90
#             default_feedback_message="" # Prevent generic BaseEvaluator feedback
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         # Start with the feedback already processed/aggregated by BaseEvaluator.
#         # It will contain actual LLM feedback or the specific default from BaseEvaluator
#         # if the LLM provided nothing.
#         if processed_result.get("feedback"):
#             final_feedback_parts.append(processed_result["feedback"])
        
#         # Add automated feedback if it's not empty
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
#         if spell_check_feedback.strip():
#             final_feedback_parts.append(spell_check_feedback)

#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are now guaranteed to be floats within 10.0-90.0 range due to BaseEvaluator scaling.
#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         form = scores_for_log.get("form", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"SummarizeWrittenText Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Form: {form:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Spelling/Punctuation: {spelling_punctuation:.2f})"
#         )

#         return processed_result



# # src/evaluators/summarize_written_text_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class SummarizeWrittenTextEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Summarize Written Text task.
#     Uses an LLM for scoring Content, Form, Grammar, Vocabulary, and Spelling & Punctuation.
#     """
#     def __init__(self):
#         super().__init__()
#         self.trait_definitions = {
#             "content": {"llm_output_max_scale": 10},
#             "form": {"llm_output_max_scale": 10},
#             "grammar": {"llm_output_max_scale": 10},
#             "vocabulary": {"llm_output_max_scale": 10},
#             "spelling_punctuation": {"llm_output_max_scale": 10},
#             "overall_score": {"llm_output_max_scale": 10}
#         }

#     def evaluate(self, passage_content: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- SummarizeWrittenTextEvaluator: Starting evaluation ---")

#         user_response = user_response.strip()

#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count == 0:
#             word_count_feedback = "⚠️ Your summary is empty. Please provide a summary."
#         elif word_count < 5:
#             word_count_feedback = f"⚠️ Summary is too short ({word_count} words). For 'Summarize Written Text', your summary must be a single sentence between 5–75 words."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Summary is too long ({word_count} words). Your summary must be a single sentence between 5–75 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (5-75 words)."

#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in SummarizeWrittenTextEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [FIX]: Make the JSON output format strictly adhere to the "scores" nesting
#         # and use the EXACT key names specified in `trait_definitions`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Summarize Written Text" task.
# The user must summarize a given passage in a single sentence, between 5 and 75 words, capturing all the main ideas.

# Passage to summarize:
# {passage_content}

# User's Summary:
# {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
# - content: Does the summary accurately identify and cover all the main ideas of the passage, without including irrelevant details?
# - form: Is the summary a single, grammatically correct sentence? (Word count is handled separately, but sentence structure is key here).
# - grammar: Are the grammatical structures accurate, varied, and complex enough for an academic summary?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for summarizing the passage, including academic terms where relevant?
# - spelling_punctuation: Are there any spelling errors or punctuation mistakes?

# Format your output EXACTLY LIKE THIS JSON. Ensure all scores are integers between 0 and 10.
# {{
#   "scores": {{
#     "content": <number>,
#     "form": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"SummarizeWrittenText LLM Prompt: {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # [FIX]: Update score_key_map to point to the nested "scores" object.
#         score_key_map = {
#             "content": {"key": "scores.content", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']},
#             "form": {"key": "scores.form", "llm_output_max_scale": self.trait_definitions['form']['llm_output_max_scale']},
#             "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
#             "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']},
#             "spelling_punctuation": {"key": "scores.spelling_punctuation", "llm_output_max_scale": self.trait_definitions['spelling_punctuation']['llm_output_max_scale']}
#         }
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10,
#             default_feedback_message=""
#         )
        
#         final_feedback_parts = []
#         if processed_result.get("feedback"):
#             final_feedback_parts.append(processed_result["feedback"])
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
#         if spell_check_feedback.strip():
#             final_feedback_parts.append(spell_check_feedback)
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         form = scores_for_log.get("form", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"SummarizeWrittenText Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Form: {form:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Spelling/Punctuation: {spelling_punctuation:.2f})"
#         )

#         return processed_result


# src/evaluators/summarize_written_text_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
from textblob import TextBlob
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SummarizeWrittenTextEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Summarize Written Text task.
    Uses an LLM for scoring Content, Form, Grammar, Vocabulary, and Spelling & Punctuation.
    """
    def __init__(self):
        super().__init__()
        # Define the raw scale the LLM is expected to output for each trait (0-10).
        self.trait_definitions = {
            "content": {"llm_output_max_scale": 10},
            "form": {"llm_output_max_scale": 10},
            "grammar": {"llm_output_max_scale": 10},
            "vocabulary": {"llm_output_max_scale": 10},
            "spelling_punctuation": {"llm_output_max_scale": 10},
            "overall_score": {"llm_output_max_scale": 10}
        }

    def evaluate(self, passage_content: str, user_response: str) -> Dict[str, Any]:
        logger.debug("--- SummarizeWrittenTextEvaluator: Starting evaluation ---")

        user_response = user_response.strip()

        # Word count feedback
        word_count = len(user_response.split())
        word_count_feedback = ""

        if word_count == 0:
            word_count_feedback = "⚠️ Your summary is empty. Please provide a summary."
        elif word_count < 5:
            word_count_feedback = f"⚠️ Summary is too short ({word_count} words). For 'Summarize Written Text', your summary must be a single sentence between 5–75 words."
        elif word_count > 75:
            word_count_feedback = f"⚠️ Summary is too long ({word_count} words). Your summary must be a single sentence between 5–75 words."
        else:
            word_count_feedback = "✅ Word count is appropriate (5-75 words)."

        spell_check_feedback = ""
        try:
            blob = TextBlob(user_response)
            misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
            if misspelled_words:
                spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
            else:
                spell_check_feedback = "✅ Spelling appears correct."
        except Exception as e:
            logger.error(f"Error during spell check in SummarizeWrittenTextEvaluator: {e}", exc_info=True)
            spell_check_feedback = "Spell check skipped due to technical issue."

        # --- Construct the instruction/prompt for the LLM ---
        # [MODIFIED]: Removed the explicit JSON format example from the user prompt.
        # BaseEvaluator will now inject a strict JSON schema into the system message.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Summarize Written Text" task.
The user must summarize a given passage in a single sentence, between 5 and 75 words, capturing all the main ideas.

Passage to summarize:
{passage_content}

User's Summary:
{user_response}

Additional Info for your consideration:
- {word_count_feedback}
- {spell_check_feedback}
- Word Count: {word_count}

Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
- content: Does the summary accurately identify and cover all the main ideas of the passage, without including irrelevant details?
- form: Is the summary a single, grammatically correct sentence? (Word count is handled separately, but sentence structure is key here).
- grammar: Are the grammatical structures accurate, varied, and complex enough for an academic summary?
- vocabulary: Is the vocabulary varied, precise, and appropriate for summarizing the passage, including academic terms where relevant?
- spelling_punctuation: Are there any spelling errors or punctuation mistakes?

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"SummarizeWrittenText LLM Prompt: {instruction[:self.max_input_length]}")

        # --- Define score key mapping ---
        score_key_map = {
            "content": {"key": "scores.content", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']},
            "form": {"key": "scores.form", "llm_output_max_scale": self.trait_definitions['form']['llm_output_max_scale']},
            "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
            "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']},
            "spelling_punctuation": {"key": "scores.spelling_punctuation", "llm_output_max_scale": self.trait_definitions['spelling_punctuation']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=10,
            default_feedback_message=""
        )
        
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        if word_count_feedback.strip():
            final_feedback_parts.append(word_count_feedback)
        if spell_check_feedback.strip():
            final_feedback_parts.append(spell_check_feedback)
        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        scores_for_log = processed_result.get("scores", {})
        content = scores_for_log.get("content", 10.0)
        form = scores_for_log.get("form", 10.0)
        grammar = scores_for_log.get("grammar", 10.0)
        vocabulary = scores_for_log.get("vocabulary", 10.0)
        spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(
            f"SummarizeWrittenText Evaluation: Overall={overall:.2f} "
            f"(Content: {content:.2f}, Form: {form:.2f}, Grammar: {grammar:.2f}, "
            f"Vocabulary: {vocabulary:.2f}, Spelling/Punctuation: {spelling_punctuation:.2f})"
        )

        return processed_result