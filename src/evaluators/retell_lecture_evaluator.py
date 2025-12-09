# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spelling check
# import re

# class RetellLectureEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Preprocessing feedback
#         user_response = user_response.strip()

#         # Word count
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Try to speak for 40–50 seconds."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it under 70 words."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

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
# You are a PTE expert evaluating the "Retell Lecture" task.

# Prompt: {prompt}
# User Said: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Key Points: Did the response capture major points from the lecture?
# - Fluency: Smoothness of expression and speech flow
# - Grammar: Sentence variety and accuracy
# - Vocabulary: Range and appropriateness of word usage
# - Relevance: Was the response directly related to the lecture?

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "key_points": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
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
#                 "key_points": 0.30,
#                 "fluency": 0.25,
#                 "grammar": 0.20,
#                 "vocabulary": 0.15,
#                 "relevance": 0.10
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

# # src/evaluators/retell_lecture_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class RetellLectureEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Retell Lecture task.
#     Uses an LLM for scoring Content, Fluency, Grammar, Vocabulary, and Relevance.
#     Integrates preprocessing for word count.
#     """
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Retell Lecture typically suggests 50-70 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please retell the lecture."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Retell Lecture', aim for 50–70 words to cover key points adequately."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 70 words, to summarize effectively."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt is updated to request the desired output format directly.
#         # Ensure all literal JSON curly braces are escaped with double curly braces {{}}
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Retell Lecture" task.
# In this task, the user must summarize the key points and main ideas of a lecture they have just heard. The response should be well-organized, coherent, and delivered fluently.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of fluency will be inferred from the textual coherence, logical organization, and completeness of the transcription.

# Lecture Summary (or key aspects to focus on): {prompt}
# User's Spoken Summary (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Content: Does the response accurately capture the major points, main ideas, and supporting details from the lecture?
# - Fluency: Is the transcription logically organized, with smooth transitions between ideas, and easy to follow, indicating a fluent delivery?
# - Grammar: Are sentence structures accurate, varied, and appropriate for summarizing an academic lecture?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for discussing the lecture's topic, including academic terms where relevant?
# - Relevance: Does the response stay focused on summarizing the lecture, avoiding irrelevant information or personal opinions?

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
#         logger.debug(f"RetellLecture LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Call BaseEvaluator for LLM Score ---
#         score_key_map = {
#             "content": {"key": "scores.content"},
#             "fluency": {"key": "scores.fluency"},
#             "grammar": {"key": "scores.grammar"},
#             "vocabulary": {"key": "scores.vocabulary"},
#             "relevance": {"key": "scores.relevance"}
#         }
#         overall_score_key = "overall_score"

#         # FIX: Tell BaseEvaluator that the LLM ACTUALLY returns 0-10 scores,
#         # despite us asking for 0-90 in the prompt. BaseEvaluator will then scale this to 0-90.
#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=10 # <-- CRITICAL FIX HERE
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         # FIX: Robustly handle LLM feedback - if it's empty or generic, provide a specific placeholder.
#         llm_output_feedback = processed_result.get("feedback", "").strip()
#         if llm_output_feedback == "No specific feedback from LLM.":
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this response.") # <-- IMPROVED DEFAULT
#         elif llm_output_feedback: # If it's not empty and not the generic string
#             final_feedback_parts.append(llm_output_feedback)
        
#         # Add automated feedback after LLM's comments
#         final_feedback_parts.append(word_count_feedback)
        
#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are already guaranteed to be floats within 10.0-90.0 range due to BaseEvaluator scaling.
#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         relevance = scores_for_log.get("relevance", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"RetellLecture Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Relevance: {relevance:.2f})"
#         )

#         return processed_result


# # src/evaluators/retell_lecture_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class RetellLectureEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Retell Lecture task.
#     Uses an LLM for scoring Content, Fluency, Grammar, Vocabulary, and Relevance.
#     Integrates preprocessing for word count.
#     """
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- RetellLectureEvaluator: Starting evaluation ---")
        
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Retell Lecture typically suggests 50-70 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please retell the lecture."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Retell Lecture', aim for 50–70 words to cover key points adequately."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 70 words, to summarize effectively."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt is updated to request the desired output format directly.
#         # IMPORTANT: While the prompt ASKS for 0-90, your LLM *returned* 0-10.
#         # We will keep the prompt asking for 0-90, but tell the BaseEvaluator
#         # that the LLM's *actual* output range is 0-10 for robust scaling.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Retell Lecture" task.
# In this task, the user must summarize the key points and main ideas of a lecture they have just heard. The response should be well-organized, coherent, and delivered fluently.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of fluency will be inferred from the textual coherence, logical organization, and completeness of the transcription.

# Lecture Summary (or key aspects to focus on): {prompt}
# User's Spoken Summary (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Content: Does the response accurately capture the major points, main ideas, and supporting details from the lecture?
# - Fluency: Is the transcription logically organized, with smooth transitions between ideas, and easy to follow, indicating a fluent delivery?
# - Grammar: Are sentence structures accurate, varied, and appropriate for summarizing an academic lecture?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for discussing the lecture's topic, including academic terms where relevant?
# - Relevance: Does the response stay focused on summarizing the lecture, avoiding irrelevant information or personal opinions?

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
#         logger.debug(f"RetellLecture LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

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

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"RetellLecture Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Relevance: {relevance:.2f})"
#         )

#         return processed_result



# # src/evaluators/retell_lecture_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class RetellLectureEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Retell Lecture task.
#     Uses an LLM for scoring Content, Fluency, Grammar, Vocabulary, and Relevance.
#     Integrates preprocessing for word count.
#     """
#     def __init__(self):
#         super().__init__()
#         self.trait_definitions = {
#             "content": {"llm_output_max_scale": 10},
#             "fluency": {"llm_output_max_scale": 10},
#             "grammar": {"llm_output_max_scale": 10},
#             "vocabulary": {"llm_output_max_scale": 10},
#             "relevance": {"llm_output_max_scale": 10},
#             "overall_score": {"llm_output_max_scale": 10}
#         }

#     def evaluate(self, lecture_content: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- RetellLectureEvaluator: Starting evaluation ---")
        
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please retell the lecture."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Retell Lecture', aim for 50–70 words to cover key points adequately."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 70 words, to summarize effectively."
#         else:
#             word_count_feedback = "✅ Response length is appropriate."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [FIX]: Make the JSON output format strictly adhere to the "scores" nesting
#         # and use the EXACT key names specified in `trait_definitions`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Retell Lecture" task.
# In this task, the user must summarize the key points and main ideas of a lecture they have just heard. The response should be well-organized, coherent, and delivered fluently.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of fluency will be inferred from the textual coherence, logical organization, and completeness of the transcription.

# Original Lecture:
# {lecture_content}

# User's Spoken Summary (transcribed):
# {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
# - content: Does the user's summary accurately capture the major points, main ideas, and supporting details from the provided lecture?
# - fluency: Is the transcription logically organized, with smooth transitions between ideas, and easy to follow, indicating a fluent delivery?
# - grammar: Are sentence structures accurate, varied, and appropriate for summarizing an academic lecture?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for discussing the lecture's topic, including academic terms where relevant?
# - relevance: Does the user's summary stay focused on the lecture, avoiding irrelevant information or personal opinions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output EXACTLY LIKE THIS JSON. Ensure all scores are integers between 0 and 10.
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
#         logger.debug(f"RetellLecture LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # [FIX]: Update score_key_map to point to the nested "scores" object.
#         score_key_map = {
#             "content": {"key": "scores.content", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']},
#             "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
#             "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
#             "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']},
#             "relevance": {"key": "scores.relevance", "llm_output_max_scale": self.trait_definitions['relevance']['llm_output_max_scale']}
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
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         scores_for_log = processed_result.get("scores", {})
#         content = scores_for_log.get("content", 10.0)
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         relevance = scores_for_log.get("relevance", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"RetellLecture Evaluation: Overall={overall:.2f} "
#             f"(Content: {content:.2f}, Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, "
#             f"Vocabulary: {vocabulary:.2f}, Relevance: {relevance:.2f})"
#         )

#         return processed_result


# src/evaluators/retell_lecture_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
from textblob import TextBlob # Keep if you still want spell check
import logging
import re

logger = logging.getLogger(__name__)

class RetellLectureEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Retell Lecture task.
    Uses an LLM for scoring Content, Fluency, Pronunciation, Vocabulary, and Grammar.
    Integrates preprocessing for word count and spell check.
    """
    def __init__(self):
        super().__init__()
        self.trait_definitions = {
            "content": {"llm_output_max_scale": 10},
            "fluency": {"llm_output_max_scale": 10},
            "pronunciation": {"llm_output_max_scale": 10},
            "vocabulary": {"llm_output_max_scale": 10},
            "grammar": {"llm_output_max_scale": 10},
            "overall_score": {"llm_output_max_scale": 10}
        }

    def evaluate(self, prompt: str, user_response: str) -> dict:
        logger.debug("--- RetellLectureEvaluator: Starting evaluation ---")
        user_response = user_response.strip()

        # --- Automated Feedback Generation ---
        word_count = len(user_response.split())
        word_count_feedback = ""

        # PTE Retell Lecture typically has a minimum word count for comprehensive summary
        if word_count < 20: # Usually aiming for 40 seconds of speech, so ~60 words. 20 is a low threshold for very poor.
            word_count_feedback = f"⚠️ Your response is too short ({word_count} words). Aim for a more comprehensive summary."
        elif word_count > 100: # Max is typically around 40 seconds, avoid very long summaries
            word_count_feedback = f"⚠️ Your response is quite long ({word_count} words). While not strictly penalized, ensure conciseness and focus on key points from the lecture."
        else:
            word_count_feedback = f"✅ Word count ({word_count} words) is appropriate for a lecture retelling."

        spell_check_feedback = ""
        try:
            blob = TextBlob(user_response)
            misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
            if misspelled_words:
                spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
            else:
                spell_check_feedback = "✅ Spelling appears correct."
        except Exception as e:
            logger.error(f"Error during spell check for RetellLecture: {e}", exc_info=True)
            spell_check_feedback = "Spell check skipped due to technical issue."

        # --- LLM Instruction (Prompt) Preparation ---
        # 'prompt' here should be the full text of the lecture.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Retell Lecture" task.
The user heard a lecture and was asked to retell it in their own words, capturing the main points.

Original Lecture:
<original_lecture>
{prompt}
</original_lecture>

User's Retelling:
<user_retelling_transcript>
{user_response}
</user_retelling_transcript>

Additional Info for your consideration (these are observations, not scores from you directly):
- {word_count_feedback}
- {spell_check_feedback}
- Word Count: {word_count}

---
**CRITICAL:** Provide your evaluation as a JSON object with the following structure.
All scores MUST be NUMERICAL values between 0 and 90. Do NOT use text like 'Excellent', 'Good', etc., for scores.
If a score is missing or cannot be determined, default to 0.

{{
  "scores": {{
    "content": <numerical_score_0-90>,
    "fluency": <numerical_score_0-90>,
    "pronunciation": <numerical_score_0-90>,
    "vocabulary": <numerical_score_0-90>,
    "grammar": <numerical_score_0-90>
  }},
  "overall_score": <numerical_overall_score_0-90>,
  "feedback": "A concise, actionable feedback string (e.g., 'The retelling effectively captured main points, but lacked fluency. Focus on pacing.')"
}}
---

Evaluate the user's response based on PTE Retell Lecture criteria:
- **Content (0-90):** How accurately and comprehensively did the user summarize the main ideas, supporting details, and relationships presented in the original lecture? Was the retelling well-organized and coherent?
- **Fluency (0-90):** How natural and smooth was the user's speech? Was there appropriate pacing, rhythm, and intonation? Were there hesitations, repetitions, or false starts?
- **Pronunciation (0-90):** How accurately did the user pronounce words? Are sounds clear? Are there any mispronunciations?
- **Vocabulary (0-90):** How varied and appropriate was the vocabulary used in the retelling of the lecture?
- **Grammar (0-90):** How accurate was the grammar and sentence structure used in the retelling?

Provide an overall score (0-90) that reflects a balanced assessment of the above criteria.
"""
        logger.debug(f"RetellLecture LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

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
            default_feedback_message="The AI model could not process your retelling for Retell Lecture due to an internal error or connection issue. Please try again."
        )

        # --- Combine LLM Feedback with Automated Feedback ---
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        
        # Only add automated feedback if LLM processed correctly or if LLM didn't provide specific feedback
        # A score > 10.0 implies successful LLM processing beyond fallback
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

        logger.info(f"RetellLecture Evaluation: Overall={overall:.2f} (Content: {content:.2f}, Fluency: {fluency:.2f}, Pronunciation: {pronunciation:.2f}, Vocab: {vocabulary:.2f}, Grammar: {grammar:.2f})")
        
        processed_result["user_response_text"] = user_response

        logger.debug("--- RetellLectureEvaluator: Finished evaluation ---")
        return processed_result