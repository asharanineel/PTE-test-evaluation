# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking

# class RespondToASituationEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Word count feedback
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         if word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). Aim for at least 50 words."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it under 70 words."
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
# You are a PTE expert evaluating the "Respond to a Situation" task.

# Situation Prompt: {prompt}
# User Response: {user_response}

# Additional Info:
# {word_count_feedback}
# {spell_check_feedback}
# Word Count: {word_count}

# Score each of these aspects on a scale of 0–90:
# - Task Achievement: Did the response fully address the situation?
# - Coherence: Is the information logically organized?
# - Fluency: Smoothness of expression, minimal pauses or repetition
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
    

#     ############### ok ########################

# # src/evaluators/respond_to_a_situation_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class RespondToASituationEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Respond to a Situation task.
#     Uses an LLM for scoring Task Achievement, Coherence, Fluency, Grammar, and Vocabulary.
#     Integrates preprocessing for word count.
#     """
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- RespondToASituationEvaluator: Starting evaluation ---")
        
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Respond to a Situation typically suggests 50-70 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please respond to the situation."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Respond to a Situation', aim for 50–70 words to fully develop your response."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 70 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate."

#         # --- Construct the instruction/prompt for the LLM ---
#         # The prompt explicitly requests the desired output format directly.
#         # Ensure all literal JSON curly braces are escaped with double curly braces {{}}
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Respond to a Situation" task.
# In this task, the user is presented with a real-life situation and must respond appropriately, providing relevant information, opinions, or solutions. The response should be well-structured, coherent, and delivered fluently.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of fluency will be inferred from the textual coherence, logical organization, and completeness of the transcription.

# Situation Prompt: {prompt}
# User's Spoken Response (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - Task Achievement: Did the response fully and appropriately address all aspects of the situation, providing relevant details or arguments?
# - Coherence and Cohesion: Is the information logically organized with clear progression of ideas and appropriate use of cohesive devices?
# - Fluency: Is the transcription logically organized, with smooth transitions between ideas, and easy to follow, indicating a fluent delivery?
# - Grammar: Are sentence structures accurate, varied, and appropriate for the context?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for discussing the situation, including relevant expressions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "Task Achievement": <number>,
#   "Coherence and Cohesion": <number>,
#   "Fluency": <number>,
#   "Grammar": <number>,
#   "Vocabulary": <number>,
#   "Overall Score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"RespondToASituation LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Call BaseEvaluator for LLM Score ---
#         # Define how to map LLM's raw JSON keys (with spaces/capitalization)
#         # to our desired standardized lowercase keys.
#         # The LLM outputs these directly on a 0-90 scale, so default_llm_output_max_scale=90 is correct.
#         score_key_map = {
#             "task_achievement": {"key": "Task Achievement"},
#             "coherence_and_cohesion": {"key": "Coherence and Cohesion"},
#             "fluency": {"key": "Fluency"},
#             "grammar": {"key": "Grammar"},
#             "vocabulary": {"key": "Vocabulary"}
#         }
#         overall_score_key = "Overall Score" 

#         processed_result = self._get_openai_score(
#             instruction=instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=90 
#         )
        
#         # --- Combine LLM Feedback with Automated Feedback ---
#         final_feedback_parts = []
        
#         llm_output_feedback = processed_result.get("feedback", "").strip()

#         # FIX: Check if the feedback from the LLM (or BaseEvaluator's aggregation) is the generic one
#         if llm_output_feedback == "No specific feedback from LLM.":
#             # Replace with a more specific default if the LLM/BaseEvaluator didn't provide anything useful
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this response.")
#         elif llm_output_feedback: # If it's not empty and not the generic string
#             final_feedback_parts.append(llm_output_feedback)
        
#         # Add automated feedback after LLM's comments
#         final_feedback_parts.append(word_count_feedback)
        
#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are already guaranteed to be floats within 10.0-90.0 range.
#         scores_for_log = processed_result.get("scores", {})
#         task_achievement = scores_for_log.get("task_achievement", 10.0)
#         coherence = scores_for_log.get("coherence_and_cohesion", 10.0) # Use the standardized key
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"RespondToASituation Evaluation: Overall={overall:.2f} "
#             f"(Task Achievement: {task_achievement:.2f}, Coherence: {coherence:.2f}, "
#             f"Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f})"
#         )

#         return processed_result




# # src/evaluators/respond_to_a_situation_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# import re
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class RespondToASituationEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Respond to a Situation task.
#     Uses an LLM for scoring Task Achievement, Coherence, Fluency, Grammar, and Vocabulary.
#     Integrates preprocessing for word count.
#     """
#     def __init__(self):
#         super().__init__()
#         # Define the raw scale the LLM is expected to output for each trait.
#         # The prompt asks for 0-90, and LLMs usually try to follow this.
#         self.trait_definitions = {
#             "task_achievement": {"llm_output_max_scale": 90},
#             "coherence_and_cohesion": {"llm_output_max_scale": 90},
#             "fluency": {"llm_output_max_scale": 90},
#             "grammar": {"llm_output_max_scale": 90},
#             "vocabulary": {"llm_output_max_scale": 90},
#             "overall_score": {"llm_output_max_scale": 90} # Assuming overall is also 0-90 from LLM
#         }

#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- RespondToASituationEvaluator: Starting evaluation ---")
        
#         # Preprocessing
#         user_response = user_response.strip()

#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
#         word_count_feedback = ""

#         # PTE guidance for Respond to a Situation typically suggests 50-70 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your response is empty. Please respond to the situation."
#         elif word_count < 50:
#             word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Respond to a Situation', aim for 50–70 words to fully develop your response."
#         elif word_count > 70:
#             word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 70 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [CRITICAL FIX]: Adjust the LLM prompt to request snake_case keys for consistency
#         # with internal mapping and to avoid reliance on flexible parsing.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Respond to a Situation" task.
# In this task, the user is presented with a real-life situation and must respond appropriately, providing relevant information, opinions, or solutions. The response should be well-structured, coherent, and delivered fluently.

# IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
# Therefore, your assessment of fluency will be inferred from the textual coherence, logical organization, and completeness of the transcription.

# Situation Prompt: {prompt}
# User's Spoken Response (transcribed): {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - Word Count: {word_count}

# Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
# - task_achievement: Did the response fully and appropriately address all aspects of the situation, providing relevant details or arguments?
# - coherence_and_cohesion: Is the information logically organized with clear progression of ideas and appropriate use of cohesive devices?
# - fluency: Is the transcription logically organized, with smooth transitions between ideas, and easy to follow, indicating a fluent delivery?
# - grammar: Are sentence structures accurate, varied, and appropriate for the context?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for discussing the situation, including relevant expressions?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 90.
# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "coherence_and_cohesion": <number>,
#     "fluency": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"RespondToASituation LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # [CRITICAL FIX]: Adjust `score_key_map` to expect the new snake_case keys directly.
#         # Explicitly use llm_output_max_scale from trait_definitions for consistency.
#         score_key_map = {
#             "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
#             "coherence_and_cohesion": {"key": "scores.coherence_and_cohesion", "llm_output_max_scale": self.trait_definitions['coherence_and_cohesion']['llm_output_max_scale']},
#             "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
#             "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
#             "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']}
#         }
#         # [CRITICAL FIX]: Adjust `overall_score_key` to expect "overall_score" as the top-level key.
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
        
#         # Start with the feedback already processed/aggregated by BaseEvaluator.
#         if processed_result.get("feedback"):
#             final_feedback_parts.append(processed_result["feedback"])
        
#         # Add automated feedback if it's not empty
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
        
#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are now guaranteed to be floats within 10.0-90.0 range.
#         scores_for_log = processed_result.get("scores", {})
#         task_achievement = scores_for_log.get("task_achievement", 10.0)
#         coherence = scores_for_log.get("coherence_and_cohesion", 10.0) 
#         fluency = scores_for_log.get("fluency", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"RespondToASituation Evaluation: Overall={overall:.2f} "
#             f"(Task Achievement: {task_achievement:.2f}, Coherence: {coherence:.2f}, "
#             f"Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f})"
#         )

#         return processed_result

# src/evaluators/respond_to_a_situation_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RespondToASituationEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Respond to a Situation task.
    Uses an LLM for scoring Task Achievement, Coherence, Fluency, Grammar, and Vocabulary.
    Integrates preprocessing for word count.
    """
    def __init__(self):
        super().__init__()
        # Define the raw scale the LLM is expected to output for each trait (0-90).
        self.trait_definitions = {
            "task_achievement": {"llm_output_max_scale": 90},
            "coherence_and_cohesion": {"llm_output_max_scale": 90},
            "fluency": {"llm_output_max_scale": 90},
            "grammar": {"llm_output_max_scale": 90},
            "vocabulary": {"llm_output_max_scale": 90},
            "overall_score": {"llm_output_max_scale": 90} # Assuming overall is also 0-90 from LLM
        }

    def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
        logger.debug("--- RespondToASituationEvaluator: Starting evaluation ---")
        
        # Preprocessing
        user_response = user_response.strip()

        # --- Automated Preprocessing and Feedback Generation ---
        word_count = len(user_response.split())
        word_count_feedback = ""

        # PTE guidance for Respond to a Situation typically suggests 50-70 words.
        if word_count == 0:
            word_count_feedback = "⚠️ Your response is empty. Please respond to the situation."
        elif word_count < 50:
            word_count_feedback = f"⚠️ Response is too short ({word_count} words). For 'Respond to a Situation', aim for 50–70 words to fully develop your response."
        elif word_count > 70:
            word_count_feedback = f"⚠️ Response is too long ({word_count} words). Keep it concise, ideally under 70 words."
        else:
            word_count_feedback = "✅ Word count is appropriate."

        # --- Construct the instruction/prompt for the LLM ---
        # [MODIFIED]: Removed the explicit JSON format example from the user prompt.
        # BaseEvaluator will now inject a strict JSON schema into the system message.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Respond to a Situation" task.
In this task, the user is presented with a real-life situation and must respond appropriately, providing relevant information, opinions, or solutions. The response should be well-structured, coherent, and delivered fluently.

IMPORTANT: You are evaluating based on a *transcription* of the user's speech.
Therefore, your assessment of fluency will be inferred from the textual coherence, logical organization, and completeness of the transcription.

Situation Prompt: {prompt}
User's Spoken Response (transcribed): {user_response}

Additional Info for your consideration:
- {word_count_feedback}
- Word Count: {word_count}

Score each of these aspects on a scale of 0–90, where 0 is completely deficient and 90 is excellent.
- task_achievement: Did the response fully and appropriately address all aspects of the situation, providing relevant details or arguments?
- coherence_and_cohesion: Is the information logically organized with clear progression of ideas and appropriate use of cohesive devices?
- fluency: Is the transcription logically organized, with smooth transitions between ideas, and easy to follow, indicating a fluent delivery?
- grammar: Are sentence structures accurate, varied, and appropriate for the context?
- vocabulary: Is the vocabulary varied, precise, and appropriate for discussing the situation, including relevant expressions?

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"RespondToASituation LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

        # --- Define score key mapping ---
        score_key_map = {
            "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
            "coherence_and_cohesion": {"key": "scores.coherence_and_cohesion", "llm_output_max_scale": self.trait_definitions['coherence_and_cohesion']['llm_output_max_scale']},
            "fluency": {"key": "scores.fluency", "llm_output_max_scale": self.trait_definitions['fluency']['llm_output_max_scale']},
            "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
            "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']}
        }
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

        processed_result = self._get_openai_score(
            instruction=instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key,
            default_llm_output_max_scale=90, # Fallback default if any key is missing or not in map
            default_feedback_message="" # Prevent generic BaseEvaluator feedback if LLM provides none
        )
        
        # --- Combine LLM Feedback with Automated Feedback ---
        final_feedback_parts = []
        if processed_result.get("feedback"):
            final_feedback_parts.append(processed_result["feedback"])
        
        if word_count_feedback.strip():
            final_feedback_parts.append(word_count_feedback)
        
        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        # --- Logging Final Scores (Crucial for debugging and verification) ---
        scores_for_log = processed_result.get("scores", {})
        task_achievement = scores_for_log.get("task_achievement", 10.0)
        coherence = scores_for_log.get("coherence_and_cohesion", 10.0) 
        fluency = scores_for_log.get("fluency", 10.0)
        grammar = scores_for_log.get("grammar", 10.0)
        vocabulary = scores_for_log.get("vocabulary", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(
            f"RespondToASituation Evaluation: Overall={overall:.2f} "
            f"(Task Achievement: {task_achievement:.2f}, Coherence: {coherence:.2f}, "
            f"Fluency: {fluency:.2f}, Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f})"
        )

        return processed_result