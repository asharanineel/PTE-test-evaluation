# from evaluators.base_evaluator import BaseEvaluator

# class WriteEssayEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         instruction = f"""
# You are a PTE expert evaluating the "Write Essay" task.
# Prompt: {prompt}
# User Wrote: {user_response}

# Score each of these aspects on a scale of 0–90:
# - Task Achievement
# - Coherence
# - Grammar
# - Vocabulary

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "coherence": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """

#         return self._get_gemini_score(instruction)

# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking


# class WriteEssayEvaluator(BaseEvaluator):
#     def evaluate(self, prompt: str, user_response: str) -> dict:
#         # Pre-processing
#         word_count = len(user_response.split())

#         # Spell checking
#         try:
#             blob = TextBlob(user_response)
#             word_ratio = len(blob.words) / len(blob.sentences) if blob.sentences else 0
#         except:
#             word_ratio = 0

#         instruction = f"""
# You are a PTE expert evaluating the "Write Essay" task.

# Prompt: {prompt}
# User Wrote: {user_response}

# Additional Info:
# - Word count: {word_count} (ideal: 200–300 words)
# - Avg words per sentence: {round(word_ratio, 2)} (ideal: 15–25)

# Score each of these aspects on a scale of 0–90:
# - Task Achievement: Did the writer fully address the topic?
# - Development, Structure & Coherence: Logical organization and progression of ideas
# - Grammar: Accuracy and variety of sentence structures
# - Vocabulary: Range and appropriateness of word usage
# - Spelling & Punctuation: Correctness of written English

# Format your output exactly like this JSON:

# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "coherence": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """

#         result = self._get_openai_score(instruction)

#         # Optional: Apply weighted average here
#         if "scores" in result:
#             scores = result["scores"]
#             weights = {
#                 "task_achievement": 0.25,
#                 "coherence": 0.25,
#                 "grammar": 0.20,
#                 "vocabulary": 0.15,
#                 "spelling_punctuation": 0.15
#             }

#             overall = sum(scores[k] * weights.get(k, 0) for k in scores if k in weights)
#             result["overall_score"] = round(overall, 1)

#         return result




# src/evaluators/write_essay_evaluator.py  8/10/25
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking
# import re
# import logging
# from typing import Dict, Any, List

# logger = logging.getLogger(__name__)

# class WriteEssayEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Write Essay task.
#     Uses an LLM for scoring Task Achievement, Development, Structure & Coherence,
#     Grammar, Vocabulary, and Spelling & Punctuation.
#     Integrates preprocessing for word count, average words per sentence, and spell check.
#     """
#     def __init__(self):
#         super().__init__()
#         # Define the raw scale the LLM is expected to output for each trait.
#         # Based on your assumption, the LLM outputs 0-10, which BaseEvaluator then scales.
#         self.trait_definitions = {
#             "task_achievement": {"llm_output_max_scale": 10},
#             "development_structure_coherence": {"llm_output_max_scale": 10},
#             "grammar": {"llm_output_max_scale": 10},
#             "vocabulary": {"llm_output_max_scale": 10},
#             "spelling_punctuation": {"llm_output_max_scale": 10},
#             "overall_score": {"llm_output_max_scale": 10} # Assuming overall is also 0-10 from LLM
#         }

#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- WriteEssayEvaluator: Starting evaluation ---")

#         # Pre-processing
#         user_response = user_response.strip()
        
#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
        
#         # Word count feedback
#         word_count_feedback = ""
#         # PTE guidance for Write Essay: 200-300 words.
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your essay is empty. Please write an essay."
#         elif word_count < 200:
#             word_count_feedback = f"⚠️ Essay is too short ({word_count} words). For 'Write Essay', aim for 200–300 words to fully develop your arguments."
#         elif word_count > 300:
#             word_count_feedback = f"⚠️ Essay is too long ({word_count} words). Keep it concise, ideally under 300 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (200-300 words)."

#         # Average words per sentence
#         avg_words_per_sentence = 0
#         avg_words_per_sentence_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             if blob.sentences: # Ensure there's at least one sentence to avoid division by zero
#                 avg_words_per_sentence = sum(len(s.words) for s in blob.sentences) / len(blob.sentences)
            
#             # PTE guidance for sentence length often implies 15-25 words as a good range.
#             if avg_words_per_sentence < 15:
#                 avg_words_per_sentence_feedback = f"⚠️ Average words per sentence is low ({round(avg_words_per_sentence, 2)}). Try to vary sentence structure and complexity."
#             elif avg_words_per_sentence > 25:
#                 avg_words_per_sentence_feedback = f"⚠️ Average words per sentence is high ({round(avg_words_per_sentence, 2)}). Consider simplifying some sentences for clarity."
#             else:
#                 avg_words_per_sentence_feedback = "✅ Average words per sentence is appropriate (15-25)."
#         except Exception as e:
#             logger.error(f"Error calculating average words per sentence in WriteEssayEvaluator: {e}", exc_info=True)
#             avg_words_per_sentence_feedback = "Average words per sentence calculation skipped due to technical issue."

#         # Spell check (relevant for writing task)
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
#             logger.error(f"Error during spell check in WriteEssayEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [CRITICAL FIX]: Change the LLM prompt to ask for scores on a 0-10 scale
#         # to match the LLM's *actual* expected output and `llm_output_max_scale`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Write Essay" task.
# The user must write an essay in response to a prompt, developing a clear argument, with logical structure, and accurate language.

# Prompt: {prompt}
# User's Essay: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {avg_words_per_sentence_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}
# - Avg words per sentence: {round(avg_words_per_sentence, 2)}

# Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
# - Task Achievement: Did the essay fully address all parts of the prompt, present a clear position, and support it with relevant arguments and examples?
# - Development_Structure_Coherence: Is the essay logically organized with a clear introduction, body paragraphs (each with a main idea and supporting details), and a conclusion? Are ideas well-developed and connected with appropriate cohesive devices?
# - Grammar: Are sentence structures accurate, varied, and complex enough for an academic essay, demonstrating good control of grammar?
# - Vocabulary: Is the vocabulary varied, precise, and appropriate for the academic topic, including a good range of academic terms?
# - Spelling_Punctuation: Are there any spelling errors or punctuation mistakes throughout the essay?

# Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.

# Format your output exactly like this JSON. Ensure all scores are integers between 0 and 10.
# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "development_structure_coherence": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"WriteEssay LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # Explicitly use llm_output_max_scale from trait_definitions for consistency.
#         score_key_map = {
#             "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
#             "development_structure_coherence": {"key": "scores.development_structure_coherence", "llm_output_max_scale": self.trait_definitions['development_structure_coherence']['llm_output_max_scale']},
#             "grammar": {"key": "scores.grammar", "llm_output_max_scale": self.trait_definitions['grammar']['llm_output_max_scale']},
#             "vocabulary": {"key": "scores.vocabulary", "llm_output_max_scale": self.trait_definitions['vocabulary']['llm_output_max_scale']},
#             "spelling_punctuation": {"key": "scores.spelling_punctuation", "llm_output_max_scale": self.trait_definitions['spelling_punctuation']['llm_output_max_scale']}
#         }
#         overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['overall_score']['llm_output_max_scale']}

#         # --- Call BaseEvaluator for LLM Score ---
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
#             final_feedback_parts.append("The AI model did not generate specific descriptive feedback for this essay. Ensure your essay fully addresses the prompt with clear arguments, logical structure, and accurate language.")
#         else:
#             final_feedback_parts.append(llm_output_feedback)
        
#         # Add automated feedback after LLM's comments
#         if word_count_feedback.strip():
#             final_feedback_parts.append(word_count_feedback)
#         if avg_words_per_sentence_feedback.strip():
#             final_feedback_parts.append(avg_words_per_sentence_feedback)
#         if spell_check_feedback.strip():
#             final_feedback_parts.append(spell_check_feedback)

#         # Join feedback, filtering out empty strings for cleaner output
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         # --- Logging Final Scores (Crucial for debugging and verification) ---
#         # Extract validated scores from processed_result for logging.
#         # These scores are now guaranteed to be floats within 10.0-90.0 range due to BaseEvaluator scaling.
#         scores_for_log = processed_result.get("scores", {})
#         task_achievement = scores_for_log.get("task_achievement", 10.0)
#         development_structure_coherence = scores_for_log.get("development_structure_coherence", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         # Log at INFO level so it appears in evaluation.log if logging level is INFO or lower
#         logger.info(
#             f"WriteEssay Evaluation: Overall={overall:.2f} "
#             f"(Task Achievement: {task_achievement:.2f}, "
#             f"Development, Structure & Coherence: {development_structure_coherence:.2f}, "
#             f"Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f}, "
#             f"Spelling/Punctuation: {spelling_punctuation:.2f})"
#         )

#         return processed_result


# # src/evaluators/write_essay_evaluator.py
# from evaluators.base_evaluator import BaseEvaluator
# from textblob import TextBlob  # For basic spell checking
# import re
# import logging
# from typing import Dict, Any, List

# logger = logging.getLogger(__name__)

# class WriteEssayEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Write Essay task.
#     Uses an LLM for scoring Task Achievement, Development, Structure & Coherence,
#     Grammar, Vocabulary, and Spelling & Punctuation.
#     Integrates preprocessing for word count, average words per sentence, and spell check.
#     """
#     def __init__(self):
#         super().__init__()
#         self.trait_definitions = {
#             "task_achievement": {"llm_output_max_scale": 10},
#             "development_structure_coherence": {"llm_output_max_scale": 10},
#             "grammar": {"llm_output_max_scale": 10},
#             "vocabulary": {"llm_output_max_scale": 10},
#             "spelling_punctuation": {"llm_output_max_scale": 10},
#             "overall_score": {"llm_output_max_scale": 10}
#         }

#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         logger.debug("--- WriteEssayEvaluator: Starting evaluation ---")

#         user_response = user_response.strip()
        
#         # --- Automated Preprocessing and Feedback Generation ---
#         word_count = len(user_response.split())
        
#         word_count_feedback = ""
#         if word_count == 0:
#             word_count_feedback = "⚠️ Your essay is empty. Please write an essay."
#         elif word_count < 200:
#             word_count_feedback = f"⚠️ Essay is too short ({word_count} words). For 'Write Essay', aim for 200–300 words to fully develop your arguments."
#         elif word_count > 300:
#             word_count_feedback = f"⚠️ Essay is too long ({word_count} words). Keep it concise, ideally under 300 words."
#         else:
#             word_count_feedback = "✅ Word count is appropriate (200-300 words)."

#         avg_words_per_sentence = 0
#         avg_words_per_sentence_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             if blob.sentences:
#                 avg_words_per_sentence = sum(len(s.words) for s in blob.sentences) / len(blob.sentences)
            
#             if avg_words_per_sentence < 15:
#                 avg_words_per_sentence_feedback = f"⚠️ Average words per sentence is low ({round(avg_words_per_sentence, 2)}). Try to vary sentence structure and complexity."
#             elif avg_words_per_sentence > 25:
#                 avg_words_per_sentence_feedback = f"⚠️ Average words per sentence is high ({round(avg_words_per_sentence, 2)}). Consider simplifying some sentences for clarity."
#             else:
#                 avg_words_per_sentence_feedback = "✅ Average words per sentence is appropriate (15-25)."
#         except Exception as e:
#             logger.error(f"Error calculating average words per sentence in WriteEssayEvaluator: {e}", exc_info=True)
#             avg_words_per_sentence_feedback = "Average words per sentence calculation skipped due to technical issue."

#         spell_check_feedback = ""
#         try:
#             blob = TextBlob(user_response)
#             misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
#             if misspelled_words:
#                 spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
#             else:
#                 spell_check_feedback = "✅ Spelling appears correct."
#         except Exception as e:
#             logger.error(f"Error during spell check in WriteEssayEvaluator: {e}", exc_info=True)
#             spell_check_feedback = "Spell check skipped due to technical issue."

#         # --- Construct the instruction/prompt for the LLM ---
#         # [FIX]: Make the JSON output format strictly adhere to the "scores" nesting
#         # and use the EXACT key names specified in `trait_definitions`.
#         instruction = f"""
# You are a highly experienced PTE expert evaluating the "Write Essay" task.
# The user must write an essay in response to a prompt, developing a clear argument, with logical structure, and accurate language.

# Prompt: {prompt}
# User's Essay: {user_response}

# Additional Info for your consideration:
# - {word_count_feedback}
# - {avg_words_per_sentence_feedback}
# - {spell_check_feedback}
# - Word Count: {word_count}
# - Avg words per sentence: {round(avg_words_per_sentence, 2)}

# Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
# - task_achievement: Did the essay fully address all parts of the prompt, present a clear position, and support it with relevant arguments and examples?
# - development_structure_coherence: Is the essay logically organized with a clear introduction, body paragraphs (each with a main idea and supporting details), and a conclusion? Are ideas well-developed and connected with appropriate cohesive devices?
# - grammar: Are sentence structures accurate, varied, and complex enough for an academic essay, demonstrating good control of grammar?
# - vocabulary: Is the vocabulary varied, precise, and appropriate for the academic topic, including a good range of academic terms?
# - spelling_punctuation: Are there any spelling errors or punctuation mistakes throughout the essay?

# Format your output EXACTLY LIKE THIS JSON. Ensure all scores are integers between 0 and 10.
# {{
#   "scores": {{
#     "task_achievement": <number>,
#     "development_structure_coherence": <number>,
#     "grammar": <number>,
#     "vocabulary": <number>,
#     "spelling_punctuation": <number>
#   }},
#   "overall_score": <number>,
#   "feedback": "<string>"
# }}
# """
#         logger.debug(f"WriteEssay LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

#         # --- Define score key mapping ---
#         # [FIX]: Update score_key_map to point to the nested "scores" object.
#         score_key_map = {
#             "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
#             "development_structure_coherence": {"key": "scores.development_structure_coherence", "llm_output_max_scale": self.trait_definitions['development_structure_coherence']['llm_output_max_scale']},
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
#         if avg_words_per_sentence_feedback.strip():
#             final_feedback_parts.append(avg_words_per_sentence_feedback)
#         if spell_check_feedback.strip():
#             final_feedback_parts.append(spell_check_feedback)
#         processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

#         scores_for_log = processed_result.get("scores", {})
#         task_achievement = scores_for_log.get("task_achievement", 10.0)
#         development_structure_coherence = scores_for_log.get("development_structure_coherence", 10.0)
#         grammar = scores_for_log.get("grammar", 10.0)
#         vocabulary = scores_for_log.get("vocabulary", 10.0)
#         spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
#         overall = processed_result.get("overall_score", 10.0)

#         logger.info(
#             f"WriteEssay Evaluation: Overall={overall:.2f} "
#             f"(Task Achievement: {task_achievement:.2f}, "
#             f"Development, Structure & Coherence: {development_structure_coherence:.2f}, "
#             f"Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f}, "
#             f"Spelling/Punctuation: {spelling_punctuation:.2f})"
#         )

#         return processed_result


# src/evaluators/write_essay_evaluator.py
from evaluators.base_evaluator import BaseEvaluator
from textblob import TextBlob  # For basic spell checking
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class WriteEssayEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Write Essay task.
    Uses an LLM for scoring Task Achievement, Development, Structure & Coherence,
    Grammar, Vocabulary, and Spelling & Punctuation.
    Integrates preprocessing for word count, average words per sentence, and spell check.
    """
    def __init__(self):
        super().__init__()
        # Define the raw scale the LLM is expected to output for each trait (0-10).
        self.trait_definitions = {
            "task_achievement": {"llm_output_max_scale": 10},
            "development_structure_coherence": {"llm_output_max_scale": 10},
            "grammar": {"llm_output_max_scale": 10},
            "vocabulary": {"llm_output_max_scale": 10},
            "spelling_punctuation": {"llm_output_max_scale": 10},
            "overall_score": {"llm_output_max_scale": 10}
        }

    def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
        logger.debug("--- WriteEssayEvaluator: Starting evaluation ---")

        user_response = user_response.strip()
        
        # --- Automated Preprocessing and Feedback Generation ---
        word_count = len(user_response.split())
        
        word_count_feedback = ""
        if word_count == 0:
            word_count_feedback = "⚠️ Your essay is empty. Please write an essay."
        elif word_count < 200:
            word_count_feedback = f"⚠️ Essay is too short ({word_count} words). For 'Write Essay', aim for 200–300 words to fully develop your arguments."
        elif word_count > 300:
            word_count_feedback = f"⚠️ Essay is too long ({word_count} words). Keep it concise, ideally under 300 words."
        else:
            word_count_feedback = "✅ Word count is appropriate (200-300 words)."

        avg_words_per_sentence = 0
        avg_words_per_sentence_feedback = ""
        try:
            blob = TextBlob(user_response)
            if blob.sentences:
                avg_words_per_sentence = sum(len(s.words) for s in blob.sentences) / len(blob.sentences)
            
            if avg_words_per_sentence < 15:
                avg_words_per_sentence_feedback = f"⚠️ Average words per sentence is low ({round(avg_words_per_sentence, 2)}). Try to vary sentence structure and complexity."
            elif avg_words_per_sentence > 25:
                avg_words_per_sentence_feedback = f"⚠️ Average words per sentence is high ({round(avg_words_per_sentence, 2)}). Consider simplifying some sentences for clarity."
            else:
                avg_words_per_sentence_feedback = "✅ Average words per sentence is appropriate (15-25)."
        except Exception as e:
            logger.error(f"Error calculating average words per sentence in WriteEssayEvaluator: {e}", exc_info=True)
            avg_words_per_sentence_feedback = "Average words per sentence calculation skipped due to technical issue."

        spell_check_feedback = ""
        try:
            blob = TextBlob(user_response)
            misspelled_words = [word for word in blob.words if word.lower() != str(TextBlob(word).correct()).lower()]
            if misspelled_words:
                spell_check_feedback = f"🟥 Spelling issues found: {', '.join(sorted(list(set(misspelled_words))))}"
            else:
                spell_check_feedback = "✅ Spelling appears correct."
        except Exception as e:
            logger.error(f"Error during spell check in WriteEssayEvaluator: {e}", exc_info=True)
            spell_check_feedback = "Spell check skipped due to technical issue."

        # --- Construct the instruction/prompt for the LLM ---
        # [MODIFIED]: Removed the explicit JSON format example from the user prompt.
        # BaseEvaluator will now inject a strict JSON schema into the system message.
        instruction = f"""
You are a highly experienced PTE expert evaluating the "Write Essay" task.
The user must write an essay in response to a prompt, developing a clear argument, with logical structure, and accurate language.

Prompt: {prompt}
User's Essay: {user_response}

Additional Info for your consideration:
- {word_count_feedback}
- {avg_words_per_sentence_feedback}
- {spell_check_feedback}
- Word Count: {word_count}
- Avg words per sentence: {round(avg_words_per_sentence, 2)}

Score each of these aspects on a scale of 0–10, where 0 is completely deficient and 10 is excellent.
- task_achievement: Did the essay fully address all parts of the prompt, present a clear position, and support it with relevant arguments and examples?
- development_structure_coherence: Is the essay logically organized with a clear introduction, body paragraphs (each with a main idea and supporting details), and a conclusion? Are ideas well-developed and connected with appropriate cohesive devices?
- grammar: Are sentence structures accurate, varied, and complex enough for an academic essay, demonstrating good control of grammar?
- vocabulary: Is the vocabulary varied, precise, and appropriate for the academic topic, including a good range of academic terms?
- spelling_punctuation: Are there any spelling errors or punctuation mistakes throughout the essay?

Also, provide a single, concise overall feedback string explaining the scores and areas for improvement.
"""
        logger.debug(f"WriteEssay LLM Prompt (truncated to {self.max_input_length} chars for log): {instruction[:self.max_input_length]}")

        # --- Define score key mapping ---
        score_key_map = {
            "task_achievement": {"key": "scores.task_achievement", "llm_output_max_scale": self.trait_definitions['task_achievement']['llm_output_max_scale']},
            "development_structure_coherence": {"key": "scores.development_structure_coherence", "llm_output_max_scale": self.trait_definitions['development_structure_coherence']['llm_output_max_scale']},
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
        if avg_words_per_sentence_feedback.strip():
            final_feedback_parts.append(avg_words_per_sentence_feedback)
        if spell_check_feedback.strip():
            final_feedback_parts.append(spell_check_feedback)
        processed_result["feedback"] = "\n".join(filter(None, final_feedback_parts))

        scores_for_log = processed_result.get("scores", {})
        task_achievement = scores_for_log.get("task_achievement", 10.0)
        development_structure_coherence = scores_for_log.get("development_structure_coherence", 10.0)
        grammar = scores_for_log.get("grammar", 10.0)
        vocabulary = scores_for_log.get("vocabulary", 10.0)
        spelling_punctuation = scores_for_log.get("spelling_punctuation", 10.0)
        overall = processed_result.get("overall_score", 10.0)

        logger.info(
            f"WriteEssay Evaluation: Overall={overall:.2f} "
            f"(Task Achievement: {task_achievement:.2f}, "
            f"Development, Structure & Coherence: {development_structure_coherence:.2f}, "
            f"Grammar: {grammar:.2f}, Vocabulary: {vocabulary:.2f}, "
            f"Spelling/Punctuation: {spelling_punctuation:.2f})"
        )

        return processed_result