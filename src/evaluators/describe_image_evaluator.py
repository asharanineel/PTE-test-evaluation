# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re

# class DescribeImageEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Preprocessing (remains the same)
#         user_response = user_response.strip()

#         # Word Count (remains the same)
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count < 35:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Aim for 40–75 words."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it under 75 words."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         # Spell Check (remains the same)
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

#         # Instruction prompt (remains the same)
#         instruction = f"""
# You are a PTE expert evaluating the "Describe Image" task.

# Prompt: {prompt}
# User Said: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Content Accuracy: Did the response accurately describe the image?
# - Fluency: Was speech smooth and uninterrupted?
# - Grammar: Were sentence structures accurate?
# - Vocabulary: Was vocabulary varied and appropriate?
# - Relevance: Did the response stay focused on the image?

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "content": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "relevance": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         # --- MODIFIED: Call the new OpenAI method from the base class ---
#         result = self._get_openai_score(instruction)

#         # Post-processing and weighted average (remains the same)
#         if "scores" in result and isinstance(result.get("scores"), dict):
#             scores = result["scores"]
#             weights = {
#                 "content": 0.30,
#                 "fluency": 0.20,
#                 "grammar": 0.15,
#                 "vocabulary": 0.15,
#                 "relevance": 0.20
#             }

#             overall = sum(scores.get(k, 0) * weights.get(k, 0) for k in weights)
#             result["overall_score"] = round(overall, 1)

#         # Append additional feedback (remains the same)
#         additional_feedback = []
#         if "feedback" in result:
#             additional_feedback.append(result["feedback"])
#         additional_feedback.append(word_count_feedback)
#         additional_feedback.append(spell_check_feedback)

#         result["feedback"] = "\n".join(additional_feedback)

#         return result

# # src/evaluators/describe_image_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging
# from typing import Dict, Any, List

# logger = logging.getLogger(__name__)

# class DescribeImageEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Describe Image task.
#     Uses an LLM for scoring content, fluency, grammar, vocabulary, and relevance.
#     Integrates pre-processing for word count and spell check.
#     """
#     def evaluate(self, description_prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- DescribeImageEvaluator: Starting evaluation ---")
        
#         # --- Automated Preprocessing and Feedback Generation ---
#         user_response = user_response.strip()
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Describe Image typically suggests 40-75 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please describe the image."
#         elif word_count < 35: # Allowing a slightly lower bound before warning for conciseness
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Aim for 40–75 words to provide sufficient detail."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 75 words."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Compare lowercase to ignore case differences when checking spelling
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in DescribeImageEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt explicitly asks for scores on a 0-90 scale and provides the structure:
#         # {"scores": {"content": <number>, ...}, "feedback": "<string>"}
#         # IMPORTANT: While the prompt ASKS for 0-90, your LLM *returned* 0-10.
#         # We will keep the prompt asking for 0-90, but tell the BaseEvaluator
#         # that the LLM's *actual* output range is 0-10 for robust scaling.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Describe Image" task.
# In this task, the user is expected to describe the main features, trends, or processes shown in an image (chart, graph, map, picture, etc.) in a clear, logical, and well-structured manner.
# The response should be concise, coherent, and use appropriate academic vocabulary.

# Image Description Context (what the image generally depicts): {description_prompt}
# User's Spoken Description (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - content: Does the response accurately identify and describe the main features, key information, and any significant trends or implications presented in the image?
# - fluency: Is the description logically organized, with smooth transitions between ideas, and easy to follow?
# - grammar: Are sentence structures accurate, varied, and complex enough for an academic description?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for describing the image, including academic terms where relevant?
# - relevance: Does the response stay focused on the image, avoiding irrelevant information or personal opinions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "content": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "relevance": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"DescribeImage LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Call BaseEvaluator for LLM Score ---
#         score_key_map = {
#             "content": {"key": "scores.content"},
#             "fluency": {"key": "scores.fluency"},
#             "grammar": {"key": "scores.grammar"},
#             "vocabulary": {"key": "scores.vocabulary"},
#             "relevance": {"key": "scores.relevance"}
#         }
#         overall_score_key = "overall_score"

#         # IMPORTANT FIX: Tell BaseEvaluator that the LLM ACTUALLY returns 0-10 scores,
#         # despite us asking for 0-90 in the prompt. BaseEvaluator will then scale this to 0-90.
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10 # FIX: LLM currently outputs 0-10, so scale it from here.
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         # FIX: Robustly handle LLM feedback - if it's empty, provide a specific placeholder.
#         llm_feedback = processed_result.get("feedback", "").strip()
#         if llm_feedback:
#             final_feedback_parts.append(llm_feedback)
#         else:
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this response.")
        
#         # Add automated feedback after LLM's comments
#         final_feedback_parts.append(word_count_feedback)
#         final_feedback_parts.append(spell_check_feedback)

#         # Join feedback, filtering out empty strings to avoid extra blank lines
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are now guaranteed to be floats within 10.0-90.0 range because BaseEvaluator scaled them.
#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         relevance = scores_for_log.get("relevance", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log
#         logger.info(
#             f"DescribeImage Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Relevance: {relevance:.2f})"
#         )

#         return processed_result


# # src/evaluators/describe_image_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging
# from typing import Dict, Any, List

# logger = logging.getLogger(__name__)

# class DescribeImageEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Describe Image task.
#     Uses an LLM for scoring content, fluency, grammar, vocabulary, and relevance.
#     Integrates pre-processing for word count and spell check.
#     """
#     def evaluate(self, description_prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- DescribeImageEvaluator: Starting evaluation ---")
        
#         # --- Automated Preprocessing and Feedback Generation ---
#         user_response = user_response.strip()
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Describe Image typically suggests 40-75 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please describe the image."
#         elif word_count < 35: # Allowing a slightly lower bound before warning for conciseness
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Aim for 40–75 words to provide sufficient detail."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 75 words."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Compare lowercase to ignore case differences when checking spelling
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in DescribeImageEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt explicitly asks for scores on a 0-90 scale and provides the structure:
#         # {"scores": {"content": <number>, ...}, "feedback": "<string>"}
#         # IMPORTANT: While the prompt ASKS for 0-90, your LLM *returned* 0-10.
#         # We will keep the prompt asking for 0-90, but tell the BaseEvaluator
#         # that the LLM's *actual* output range is 0-10 for robust scaling.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Describe Image" task.
# In this task, the user is expected to describe the main features, trends, or processes shown in an image (chart, graph, map, picture, etc.) in a clear, logical, and well-structured manner.
# The response should be concise, coherent, and use appropriate academic vocabulary.

# Image Description Context (what the image generally depicts): {description_prompt}
# User's Spoken Description (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - content: Does the response accurately identify and describe the main features, key information, and any significant trends or implications presented in the image?
# - fluency: Is the description logically organized, with smooth transitions between ideas, and easy to follow?
# - grammar: Are sentence structures accurate, varied, and complex enough for an academic description?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for describing the image, including academic terms where relevant?
# - relevance: Does the response stay focused on the image, avoiding irrelevant information or personal opinions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "content": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "relevance": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"DescribeImage LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # These keys directly correspond to the expected structure in normalized_llm_output["scores"]
#         score_key_map = {
#             "content": {"key": "content"}, # Simple key expected in normalized_llm_output["scores"]
#             "fluency": {"key": "fluency"},
#             "grammar": {"key": "grammar"},
#             "vocabulary": {"key": "vocabulary"},
#             "relevance": {"key": "relevance"}
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

#         # Join feedback, filtering out empty strings to avoid extra blank lines
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are now guaranteed to be floats within 10.0-90.0 range because BaseEvaluator scaled them.
#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         relevance = scores_for_log.get("relevance", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log
#         logger.info(
#             f"DescribeImage Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Relevance: {relevance:.2f})"
#         )

#         return processed_result


# # src/evaluators/describe_image_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob
# import re
# import logging
# from typing import Dict, Any, List

# logger = logging.getLogger(__name__)

# class DescribeImageEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Describe Image task.
#     Uses an LLM for scoring content, fluency, grammar, vocabulary, and relevance.
#     Integrates pre-processing for word count and spell check.
#     """
#     def __init__(self):
#         super().__init__()
#         # Define the raw scale the LLM is expected to output for each trait.
#         # If your LLM is *actually* outputting 0-10, this is the place to state it.
#         self.trait_definitions = {
#             "content": {"llm_output_max_scale": 10},
#             "fluency": {"llm_output_max_scale": 10},
#             "grammar": {"llm_output_max_scale": 10},
#             "vocabulary": {"llm_output_max_scale": 10},
#             "relevance": {"llm_output_max_scale": 10},
#             "overall_score": {"llm_output_max_scale": 10} # Assuming overall is also 0-10 from LLM
#         }

#     def evaluate(self, description_prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- DescribeImageEvaluator: Starting evaluation ---")
        
#         # --- Automated Preprocessing and Feedback Generation ---
#         user_response = user_response.strip()
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Describe Image typically suggests 40-75 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please describe the image."
#         elif word_count < 35: # Allowing a slightly lower bound before warning for conciseness
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Aim for 40–75 words to provide sufficient detail."
#         elif word_count > 75:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 75 words."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             # Compare lowercase to ignore case differences when checking spelling
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in DescribeImageEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [CRITICAL FIX]: Change the LLM prompt to ask for scores on a 0-10 scale
#         # to match the LLM's *actual* expected output and `llm_output_max_scale`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Describe Image" task.
# In this task, the user is expected to describe the main features, trends, or processes shown in an image (chart, graph, map, picture, etc.) in a clear, logical, and well-structured manner.
# The response should be concise, coherent, and use appropriate academic vocabulary.

# Image Description Context (what the image generally depicts): {description_prompt}
# User's Spoken Description (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
# - content: Does the response accurately identify and describe the main features, key information, and any significant trends or implications presented in the image?
# - fluency: Is the description logically organized, with smooth transitions between ideas, and easy to follow?
# - grammar: Are sentence structures accurate, varied, and complex enough for an academic description?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for describing the image, including academic terms where relevant?
# - relevance: Does the response stay focused on the image, avoiding irrelevant information or personal opinions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 10.
# {{
#   "scores": {{
#     "content": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "relevance": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"DescribeImage LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # Each score mapping now explicitly uses the max scale from trait_definitions.
#         score_key_map = {
#             "content": {"key": "scores.content", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']},
#             "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
#             "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
#             "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']},
#             "relevance": {"key": "scores.relevance", "llm_output_max_scale": self.trait_definitions['relevance']['llm_output_max_scale']}
#         }
#         # The overall_score_key also needs to specify its max scale
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

#         # --- Call BaseEvaluator for LLM Score ---
#         # No need for default_llm_output_max_scale here as it's specified per key in score_key_map and overall_score_key.
#         # However, it's good practice to provide it if *any* score might fall back to the default processing.
#         # Let's keep it as 10 to be explicit about what the LLM *is supposed to* output if keys aren't matched.
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10, # Fallback/default for any key not specified in score_key_map/overall_score_key
#             default_feedback_message="" # Prevent generic BaseEvaluator feedback if LLM provides none
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

#         # Join feedback, filtering out empty strings to avoid extra blank lines
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are now guaranteed to be floats within 10.0-90.0 range because BaseEvaluator scaled them.
#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         relevance = scores_for_log.get("relevance", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log
#         logger.info(
#             f"DescribeImage Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Relevance: {relevance:.2f})"
#         )

#         return processed_result



# src/evaluators/describe_image_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
from textblob import TextBlob
import logging
import re

logger = logging.getLogger(__name__)

class DescribeImageEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Describe Image task.
    Uses an LLM for scoring Content, Fluency, Pronunciation, Vocabulary, and Grammar.
    Integrates preprocessing for word count and spell check.
    """
    def __init__(self):
        super().__init__()
        self.trait_definitions = {
            "content": {"llm_output_max_scale": 90},
            "fluency": {"llm_output_max_scale": 90},
            "pronunciation": {"llm_output_max_scale": 90},
            "vocabulary": {"llm_output_max_scale": 90},
            "grammar": {"llm_output_max_scale": 90},
            "overall_score": {"llm_output_max_scale": 90}
        }

    def evaluate(self, prompt: str, user_response: str) -> dict:
        logger.debug("--- DescribeImageEvaluator: Starting evaluation ---")
        user_response = user_response.strip()

        # --- Automated Feedback Generation ---
        word_count = len(user_response.split())
        word_count_feedback = ""

        if word_count < 20:
            word_count_feedback = f"⚠️ Your response is too short ({word_count} words). Aim for 25-40 words for a good description."
        elif word_count > 40: # PTE guideline for DI is typically 40 seconds, leading to ~60-75 words at speaking speed
            word_count_feedback = f"⚠️ Your response is quite long ({word_count} words). While not strictly penalized, ensure conciseness and focus on key points."
        else:
            word_count_feedback = f"✅ Word count ({word_count} words) is appropriate."

        spell_check_feedback = ""
        try:
            blob = TextBlob(user_response)
            misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
            if misspelled_words:
                spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
            else:
                spell_check_feedback = "✅ Spelling appears correct."
        except Exception as e:
            logger.error(f"Error during spell check for DescribeImage: {e}", exc_info=True)
            spell_check_feedback = "Spell check skipped due to technical issue."

        # --- LLM Instruction (Prompt) Preparation ---
        # 'prompt' here should contain the description or key elements of the image, or simply be a placeholder.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Describe Image" task.
The user was shown an image (context: "{prompt}") and asked to describe it. Your evaluation should focus on how well the user orally described the image based on PTE criteria.

User's Description: {user_response}

Additional Info for your consideration (these are observations, not scores from you directly):
- {word_count_feedback}
- {spell_check_feedback}
- Word Count: {word_count}

Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
- Content: How accurately and completely did the user identify and describe the key features and implied trends/information in the image? Was the description logical, well-structured, and easy to follow? (0-90)
- Fluency: How natural and smooth was the user's speech? Was there appropriate pacing, rhythm, and intonation? Were there hesitations, repetitions, or false starts? (0-90)
- Pronunciation: How accurately did the user pronounce words? Are sounds clear? Are there any mispronunciations? (0-90)
- Vocabulary: How varied and appropriate was the vocabulary used to describe the image's elements and relationships? (0-90)
- Grammar: How accurate was the grammar and sentence structure used in the description? (0-90)

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"DescribeImage LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

        # --- Call BaseEvaluator for LLM Score ---
        score_key_map = {
            "content": {"key": "scores.content", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']},
            "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
            "pronunciation": {"key": "scores.pronunciation", "llm_output_max_scale": self.trait_definitions['pronunciation']['llm_output_max_scale']},
            "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']},
            "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=90,
            default_feedback_message="The AI model could not process your description for Describe Image due to an internal error or connection issue. Please try again."
        )

        # --- Combine LLM Feedback with Automated Feedback ---
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        
        if processed_result.get("overall_score", 0) > 10.0 or not processed_result.get("feedback"):
             final_feedback_parts.append(word_count_feedback)
             final_feedback_parts.append(spell_check_feedback)

        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        # --- Logging Final Scores ---
        scores_for_log = processed_result.get("scores", {})
        content = scores_for_log.get("content", 10.0)
        fluency = scores_for_log.get("fluency", 10.0)
        pronunciation = scores_for_log.get("pronunciation", 10.0)
        vocabulary = scores_for_log.get("vocabulary", 10.0)
        grammar = scores_for_log.get("grammar", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(f"DescribeImage Evaluation: Overall={overall:.2f} (Content: {content:.2f}, Fluency: {fluency:.2f}, Pronunciation: {pronunciation:.2f}, Vocab: {vocabulary:.2f}, Grammar: {grammar:.2f})")
        
        processed_result["user_response_text"] = user_response

        logger.debug("--- DescribeImageEvaluator: Finished evaluation ---")
        return processed_result