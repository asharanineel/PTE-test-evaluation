
# this code giving good result 

# import os
# import json
# import logging
# import statistics
# import tempfile
# import time
# import re
# from typing import List, Dict, Optional, Any, Tuple, Union

# # Import BaseEvaluator
# from evaluators.base_evaluator import BaseEvaluator
# from config import settings

# import whisper 

# logger = logging.getLogger(__name__)

# class SummarizeGroupDiscussionEvaluator(BaseEvaluator):
#     """
#     Evaluator for the PTE Summarize Group Discussion task.
#     It uses the UPLOADED AUDIO FILE (transcribed by LOCAL WHISPER) for all evaluations:
#     Content, Oral Fluency, and Pronunciation.
#     It leverages BaseEvaluator for robust LLM interaction and score processing.
#     """

#     def __init__(self):
#         # Call BaseEvaluator's __init__ to set up OpenAI client, retries, etc.
#         super().__init__() 
        
#         # Define max marks for internal (non-LLM) traits. LLM traits will be 0-90 after BaseEvaluator scales them.
#         self.trait_definitions = {
#             "Content": {"max_marks_raw": 6, "contribution": "Clear summary of discussion; all main ideas included; different speakers’ points noted; well-organized; paraphrased."},
#             "Oral Fluency": {"max_marks_raw": 5, "contribution": "Smooth, natural pace; minimal hesitation; consistent rhythm; few disfluencies."},
#             "Pronunciation": {"max_marks_raw": 5, "contribution": "Clarity of speech; intelligibility; correct stress/intonation; ability to be understood by listeners even with accent."}
#         }

#         self.whisper_model = None
#         try:
#             logger.info(f"Loading local Whisper model: {settings.WHISPER_MODEL_SIZE}...")
#             if not hasattr(self.__class__, '_whisper_model_instance') or self.__class__._whisper_model_instance is None:
#                 self.__class__._whisper_model_instance = whisper.load_model(settings.WHISPER_MODEL_SIZE)
#             self.whisper_model = self.__class__._whisper_model_instance
#             logger.info(f"Local Whisper model '{settings.WHISPER_MODEL_SIZE}' loaded successfully.")
#         except Exception as e:
#             logger.error(f"Failed to load local Whisper model '{settings.WHISPER_MODEL_SIZE}': {e}", exc_info=True)
#             logger.warning("Local Whisper STT will be unavailable. Fluency and Pronunciation will be scored 10.")
        
#         self.gemini_api_key = settings.GEMINI_API_KEY
#         self.dashscope_api_key = settings.DASHSCOPE_API_KEY
#         self.dashscope_model_name = settings.DASHSCOPE_MODEL_NAME
#         self.llm_base_url = settings.LLM_BASE_URL


#     def evaluate(self, discussion_data: List[Dict], audio_file_stream: bytes, topic: Optional[str] = None, llm_provider: str = "openai") -> Dict[str, Any]:
        
#         audio_transcript = ""
#         words_details = []
#         stt_unavailable_feedback = ""
        
#         # --- 1. Audio Transcription (Whisper) ---
#         if self.whisper_model:
#             try:
#                 # This is the line causing the AttributeError if the method is not loaded
#                 audio_transcript, words_details = self._transcribe_audio_whisper(audio_file_stream)
#                 if not audio_transcript: # If transcription returns empty text
#                     stt_unavailable_feedback = "Whisper transcribed an empty response. "
#             except RuntimeError as e:
#                 logger.error(f"Error during local Whisper audio transcription: {e}", exc_info=True)
#                 stt_unavailable_feedback = f"Local Whisper transcription failed: {e}. "
#         else:
#             stt_unavailable_feedback = "Local Whisper STT model not loaded. "

#         # --- 2. Calculate Raw Scores (0-5 or 0-6 scale) ---
#         raw_content_score = 0
#         raw_fluency_score = 0
#         raw_pron_score = 0
        
#         fluency_info = ""
#         pron_info = ""
#         content_feedback_llm = "" # LLM's direct content feedback

#         if stt_unavailable_feedback:
#             # If STT is unavailable or transcript is empty, all raw scores are 0.
#             # Feedback reflects this. BaseEvaluator's _validate_score_value will clamp these to 10.
#             fluency_info = stt_unavailable_feedback + "No speech detected or STT unavailable for fluency evaluation."
#             pron_info = stt_unavailable_feedback + "No speech detected or STT unavailable for pronunciation evaluation."
#             content_feedback_llm = stt_unavailable_feedback + "No speech detected or STT unavailable for content evaluation."
#             logger.warning("STT unavailable or empty transcript. All scores defaulting to minimum.")
#         else:
#             raw_fluency_score, fluency_info = self._evaluate_fluency(words_details)
#             raw_pron_score, pron_info = self._evaluate_pronunciation(words_details)
            
#             # --- Call LLM for Content Score (0-6 scale) ---
#             content_llm_processed_result = self._get_llm_content_score_internal(
#                 discussion_data, audio_transcript, topic, llm_provider
#             )
#             raw_content_score = content_llm_processed_result.get("content_score_raw", 0) # Raw score 0-6
#             content_feedback_llm = content_llm_processed_result.get("content_feedback", "") 
            
#             # If the LLM call itself failed (e.g., JSON parse error for content),
#             # the _get_llm_content_score_internal would return a score 0.
#             # We add its feedback to the main content_feedback.
#             if raw_content_score == 0 and "LLM evaluation failed" in content_feedback_llm: 
#                 logger.warning(f"Content LLM call failed or returned 0: {content_feedback_llm}")
#             elif not content_feedback_llm.strip():
#                  content_feedback_llm = "The AI model did not generate specific descriptive feedback for content."


#         # --- 3. Validate and Scale Scores to PTE (10-90) using BaseEvaluator's logic ---
#         # This is where we use _validate_score_value to handle normalization and clamping.

#         # Content score (raw 0-6, scaled to 10-90)
#         pte_content_score = self._validate_score_value(raw_content_score, self.trait_definitions['Content']['max_marks_raw'])
        
#         # Fluency score (raw 0-5, scaled to 10-90)
#         pte_oral_fluency_score = self._validate_score_value(raw_fluency_score, self.trait_definitions['Oral Fluency']['max_marks_raw'])

#         # Pronunciation score (raw 0-5, scaled to 10-90)
#         pte_pronunciation_score = self._validate_score_value(raw_pron_score, self.trait_definitions['Pronunciation']['max_marks_raw'])
        
#         # --- 4. Calculate Overall PTE Score ---
#         # Sum the already PTE-scaled individual scores.
#         sum_pte_scores = pte_content_score + pte_oral_fluency_score + pte_pronunciation_score
        
#         # Average these 3 scores to get an overall PTE score, then clamp
#         pte_overall_score = round(sum_pte_scores / 3) if sum_pte_scores > 0 else 10.0
#         pte_overall_score = max(10.0, min(90.0, pte_overall_score)) 


#         # --- 5. Aggregate Comprehensive Feedback ---
#         comprehensive_feedback_parts = [
#             "--- Overall Summary Feedback ---",
#             f"Content: {content_feedback_llm}", 
#             f"Oral Fluency: {fluency_info}",
#             f"Pronunciation: {pron_info}",
#             "", 
#             "Overall Recommendation: Focus on improving areas with lower scores."
#         ]
        
#         # Add specific recommendations based on PTE scaled scores
#         if pte_content_score < 50: 
#             comprehensive_feedback_parts.append("Specifically, work on accurately capturing main ideas and organizing your summary for content.")
#         if pte_oral_fluency_score < 50:
#             comprehensive_feedback_parts.append("For oral fluency, practice speaking at a natural pace with fewer hesitations.")
#         if pte_pronunciation_score < 50:
#             comprehensive_feedback_parts.append("For pronunciation, focus on clarity, correct stress, and intonation.")
        
#         comprehensive_feedback = "\n".join(comprehensive_feedback_parts)

#         # --- 6. Logging Final Scores ---
#         logger.info(
#             f"SummarizeGroupDiscussion Evaluation: Final Evaluation (PTE Scaled): Overall={pte_overall_score:.2f} "
#             f"(Content: {pte_content_score:.2f}, Oral Fluency: {pte_oral_fluency_score:.2f}, Pronunciation: {pte_pronunciation_score:.2f})"
#         )

#         # --- 7. Return Final Result Dictionary ---
#         return {
#             "scores": {
#                 "content": pte_content_score,
#                 "oral_fluency": pte_oral_fluency_score,
#                 "pronunciation": pte_pronunciation_score,
#             },
#             "overall_score": pte_overall_score, 
#             "feedback": comprehensive_feedback,
#             "audio_transcript": audio_transcript, 
#         }

#     # --- Transcribe Audio (This method is correctly defined here) ---
#     def _transcribe_audio_whisper(self, audio_file_stream: bytes) -> tuple[str, List[Dict]]:
#         """
#         Transcribes audio using local OpenAI Whisper model from a byte stream.
#         It saves the stream to a temporary file for Whisper to process.
#         """
#         if not self.whisper_model:
#             logger.warning("Local Whisper model not loaded. Skipping transcription.")
#             return "", []

#         logger.info("Transcribing audio with Whisper from byte stream.")
        
#         temp_file = None
#         try:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
#                 temp_file.write(audio_file_stream)
            
#             temp_file_path = temp_file.name
            
#             result = self.whisper_model.transcribe(temp_file_path, word_timestamps=True)
            
#             full_transcript = result.get("text", "").strip()
#             words_details = []

#             if "segments" in result:
#                 for segment in result["segments"]:
#                     if "words" in segment:
#                         for word_data in segment["words"]:
#                             words_details.append({
#                                 "word": word_data["word"].strip(),
#                                 "start_time": word_data["start"],
#                                 "end_time": word_data["end"],
#                                 "confidence": word_data.get("probability", 1.0),
#                             })
            
#             logger.info(f"Whisper transcription complete. Length: {len(full_transcript)} chars, Words: {len(words_details)}")
#             return full_transcript, words_details
#         except Exception as e:
#             logger.error(f"Local Whisper transcription failed from stream: {e}", exc_info=True)
#             raise RuntimeError(f"Whisper transcription error: {e}")
#         finally:
#             if temp_file and os.path.exists(temp_file.name):
#                 os.remove(temp_file.name)
#                 logger.debug(f"Removed temporary audio file: {temp_file.name}")

#     def _evaluate_fluency(self, words_details: List[Dict]) -> Tuple[int, str]:
#         if not words_details:
#             return 0, "No speech detected for fluency evaluation."
        
#         total_speaking_duration = 0
#         if words_details:
#             total_speaking_duration = words_details[-1]["end_time"] - words_details[0]["start_time"]
        
#         wpm = (len(words_details) / total_speaking_duration) * 60 if total_speaking_duration > 0 else 0

#         pauses = []
#         for i in range(1, len(words_details)):
#             pause = words_details[i]["start_time"] - words_details[i - 1]["end_time"]
#             if pause > 0.5: 
#                 pauses.append(pause)
        
#         avg_pause = statistics.mean(pauses) if pauses else 0

#         fluency_score = 5 
#         feedback_parts = []

#         # WPM scoring
#         if wpm < 100:
#             fluency_score -= 1
#             feedback_parts.append("Speaking rate is a bit slow (below 100 WPM).")
#         elif wpm > 180:
#             fluency_score -= 1
#             feedback_parts.append("Speaking rate is too fast (above 180 WPM).")
#         else:
#             feedback_parts.append("Speaking rate is appropriate (100-180 WPM).")

#         # Pause scoring
#         if avg_pause > 1.0:
#             fluency_score -= 2
#             feedback_parts.append("Frequent long pauses detected (avg > 1.0s), affecting smoothness.")
#         elif avg_pause > 0.5:
#             fluency_score -= 1
#             feedback_parts.append("Some pauses detected (avg > 0.5s), could improve flow.")
#         else:
#             feedback_parts.append("Minimal pauses, good flow.")

#         fluency_score = max(0, min(5, fluency_score)) 

#         info_string = f"WPM={int(wpm)}, Avg Pause={round(avg_pause,2)}s. {' '.join(feedback_parts)}"
#         return fluency_score, info_string


#     def _evaluate_pronunciation(self, words_details: List[Dict]) -> Tuple[int, str]:
#         if not words_details:
#             return 0, "No speech detected for pronunciation evaluation."
        
#         confidences = [w["confidence"] for w in words_details if w.get("confidence", 0) > 0]
#         avg_conf = statistics.mean(confidences) if confidences else 0

#         if avg_conf >= 0.9:
#             score = 5
#             feedback = "Excellent clarity and intelligibility."
#         elif avg_conf >= 0.8:
#             score = 4
#             feedback = "Good clarity, generally easy to understand."
#         elif avg_conf >= 0.7:
#             score = 3
#             feedback = "Fair clarity, some words might be unclear."
#         elif avg_conf >= 0.6:
#             score = 2
#             feedback = "Limited clarity, noticeable difficulty in understanding."
#         else:
#             score = 1
#             feedback = "Very low clarity, difficult to understand."

#         score = max(0, min(5, score)) 
#         info_string = f"Avg confidence={round(avg_conf,2)}. {feedback}"
#         return score, info_string

#     def _get_llm_content_score_internal(self,
#         discussion_data: List[Dict],
#         user_summary_text: str,
#         topic: Optional[str],
#         provider: str = "openai" 
#     ) -> Dict[str, Union[int, str]]:
        
#         discussion_text = "\n".join([f"{d['speaker']}: {d['text']}" for d in discussion_data])
        
#         prompt_instruction = f"""
# You are a PTE Academic evaluator.
# Task: Score the user's summary of a group discussion for CONTENT.

# Topic: {topic if topic else 'N/A'}

# Original Discussion Transcript:
# {discussion_text}

# User's Summary (transcribed from audio):
# {user_summary_text}

# Scoring (0-6) for Content:
# - 6 = Clear, complete summary; all main ideas included; different speakers’ points noted; well-organized; paraphrased.
# - 3 = Some main ideas missing or copied directly; weak organization.
# - 0 = Off-topic, mostly irrelevant, or no response.

# Return JSON with fields:
# {{
#   "content_score": <0-6>,
#   "content_feedback": "<short and specific feedback for content improvement>"
# }}
# """
#         logger.debug(f"SummarizeGroupDiscussion Content LLM Prompt (truncated): {prompt_instruction[:self.max_input_length]}")
        
#         score_key_map = {
#             "content_score": {"key": "content_score", "llm_output_max_scale": self.trait_definitions['Content']['max_marks_raw']}
#         }
#         overall_score_key = "content_score" 
        
#         if provider != "openai":
#             logger.warning(f"SummarizeGroupDiscussion: LLM Provider '{provider}' requested, but BaseEvaluator defaults to OpenAI API. Falling back to OpenAI call.")

#         processed_llm_output = self._get_openai_score(
#             instruction=prompt_instruction,
#             score_key_map=score_key_map,
#             overall_score_key=overall_score_key,
#             default_llm_output_max_scale=self.trait_definitions['Content']['max_marks_raw'], 
#             default_feedback_message="" 
#         )

#         scaled_content_score_from_llm = processed_llm_output.get("overall_score", 0.0)

#         max_marks_raw_content = self.trait_definitions['Content']['max_marks_raw']
#         reverse_scaled_content_score = (scaled_content_score_from_llm * max_marks_raw_content) / 90.0
        
#         reverse_scaled_content_score = max(0, min(max_marks_raw_content, round(reverse_scaled_content_score)))

#         llm_content_feedback = processed_llm_output.get("feedback", "").strip()
#         if not llm_content_feedback:
#             llm_content_feedback = "The AI model did not generate specific descriptive feedback for content."
#         elif llm_content_feedback == "No specific feedback from LLM.": 
#              llm_content_feedback = "The AI model did not generate specific descriptive feedback for content."


#         return {
#             "content_score_raw": reverse_scaled_content_score, 
#             "content_feedback": llm_content_feedback 
#         }


# latest modified code 
import os
import json
import logging
import statistics
import tempfile
import time
import re
from typing import List, Dict, Optional, Any, Tuple, Union

# Import BaseEvaluator
from evaluators.base_evaluator import BaseEvaluator
from config import settings

import whisper 

logger = logging.getLogger(__name__)

class SummarizeGroupDiscussionEvaluator(BaseEvaluator):
    """
    Evaluator for the PTE Summarize Group Discussion task.
    It uses the UPLOADED AUDIO FILE (transcribed by LOCAL WHISPER) for all evaluations:
    Content, Oral Fluency, and Pronunciation.
    It leverages BaseEvaluator for robust LLM interaction and score processing.
    """

    def __init__(self):
        # Call BaseEvaluator's __init__ to set up OpenAI client, retries, etc.
        super().__init__() 
        
        # Define the raw scale for each trait.
        # 'content' is LLM-evaluated and we expect it to return 0-6.
        # 'oral_fluency' and 'pronunciation' are internally calculated on a 0-5 scale.
        self.trait_definitions = {
            "content": {"llm_output_max_scale": 6}, # LLM outputs on 0-6 scale for content
            "oral_fluency": {"max_marks_raw": 5},   # Internal calculation is 0-5
            "pronunciation": {"max_marks_raw": 5},  # Internal calculation is 0-5
            # Overall score does not have a raw scale from LLM in this mixed scenario,
            # as it's an average of PTE-scaled sub-scores.
        }

        self.whisper_model = None
        try:
            logger.info(f"Loading local Whisper model: {settings.WHISPER_MODEL_SIZE}...")
            if not hasattr(self.__class__, '_whisper_model_instance') or self.__class__._whisper_model_instance is None:
                self.__class__._whisper_model_instance = whisper.load_model(settings.WHISPER_MODEL_SIZE)
            self.whisper_model = self.__class__._whisper_model_instance
            logger.info(f"Local Whisper model '{settings.WHISPER_MODEL_SIZE}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load local Whisper model '{settings.WHISPER_MODEL_SIZE}': {e}", exc_info=True)
            logger.warning("Local Whisper STT will be unavailable. Fluency and Pronunciation will be scored 10.")
        
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.dashscope_api_key = settings.DASHSCOPE_API_KEY
        self.dashscope_model_name = settings.DASHSCOPE_MODEL_NAME
        self.llm_base_url = settings.LLM_BASE_URL


    def evaluate(self, discussion_data: List[Dict], audio_file_stream: bytes, topic: Optional[str] = None, llm_provider: str = "openai") -> Dict[str, Any]:
        logger.debug("--- SummarizeGroupDiscussionEvaluator: Starting evaluation ---")

        audio_transcript = ""
        words_details = []
        stt_unavailable_feedback = ""
        
        # --- 1. Audio Transcription (Whisper) ---
        if self.whisper_model:
            try:
                audio_transcript, words_details = self._transcribe_audio_whisper(audio_file_stream)
                if not audio_transcript:
                    stt_unavailable_feedback = "Whisper transcribed an empty response. "
            except RuntimeError as e:
                logger.error(f"Error during local Whisper audio transcription: {e}", exc_info=True)
                stt_unavailable_feedback = f"Local Whisper transcription failed: {e}. "
        else:
            stt_unavailable_feedback = "Local Whisper STT model not loaded. "

        # --- 2. Calculate Scores (Internal & LLM) ---
        raw_fluency_score = 0
        raw_pron_score = 0
        
        fluency_info = ""
        pron_info = ""
        content_feedback_llm = ""
        pte_content_score = 10.0 # Default to minimum PTE score

        if stt_unavailable_feedback:
            fluency_info = stt_unavailable_feedback + "No speech detected or STT unavailable for fluency evaluation."
            pron_info = stt_unavailable_feedback + "No speech detected or STT unavailable for pronunciation evaluation."
            content_feedback_llm = stt_unavailable_feedback + "No speech detected or STT unavailable for content evaluation."
            logger.warning("STT unavailable or empty transcript. All scores defaulting to minimum.")
        else:
            # Internal Fluency & Pronunciation calculations
            raw_fluency_score, fluency_info = self._evaluate_fluency(words_details)
            raw_pron_score, pron_info = self._evaluate_pronunciation(words_details)
            
            # --- Call LLM for Content Score ---
            content_llm_result = self._get_llm_content_score_internal(
                discussion_data, audio_transcript, topic, llm_provider
            )
            # [MODIFIED]: _get_llm_content_score_internal now returns the PTE-scaled content score directly.
            pte_content_score = content_llm_result.get("pte_content_score", 10.0)
            content_feedback_llm = content_llm_result.get("content_feedback", "") 
            
            if pte_content_score == 10.0 and "LLM evaluation failed" in content_feedback_llm: 
                logger.warning(f"Content LLM call failed or returned 0: {content_feedback_llm}")
            elif not content_feedback_llm.strip():
                 content_feedback_llm = "The AI model did not generate specific descriptive feedback for content."


        # --- 3. Scale Internal Scores to PTE (10-90) ---
        # PTE-scale internal fluency score (raw 0-5 -> 10-90)
        pte_oral_fluency_score = self._validate_score_value(raw_fluency_score, self.trait_definitions['oral_fluency']['max_marks_raw'])

        # PTE-scale internal pronunciation score (raw 0-5 -> 10-90)
        pte_pronunciation_score = self._validate_score_value(raw_pron_score, self.trait_definitions['pronunciation']['max_marks_raw'])
        
        # --- 4. Calculate Overall PTE Score (Average of the 3 PTE-scaled scores) ---
        sum_pte_scores = pte_content_score + pte_oral_fluency_score + pte_pronunciation_score
        
        # Average these 3 scores to get an overall PTE score, then clamp
        # Ensure division is only if there are actual scores to average (not just defaults).
        num_evaluated_scores = sum(1 for s in [pte_content_score, pte_oral_fluency_score, pte_pronunciation_score] if s > 10.0) # Check if actual score is > min default
        if num_evaluated_scores > 0:
             pte_overall_score = round(sum_pte_scores / 3) # Always divide by 3 categories, even if some defaulted to 10
        else:
             pte_overall_score = 10.0 # If all defaulted, overall is also default min
        
        pte_overall_score = max(10.0, min(90.0, pte_overall_score)) 


        # --- 5. Aggregate Comprehensive Feedback ---
        comprehensive_feedback_parts = [
            "--- Overall Summary Feedback ---",
            f"Content: {content_feedback_llm}", 
            f"Oral Fluency: {fluency_info}",
            f"Pronunciation: {pron_info}",
            "", 
            "Overall Recommendation: Focus on improving areas with lower scores."
        ]
        
        # Add specific recommendations based on PTE scaled scores
        if pte_content_score < 50: 
            comprehensive_feedback_parts.append("Specifically, work on accurately capturing main ideas and organizing your summary for content.")
        if pte_oral_fluency_score < 50:
            comprehensive_feedback_parts.append("For oral fluency, practice speaking at a natural pace with fewer hesitations.")
        if pte_pronunciation_score < 50:
            comprehensive_feedback_parts.append("For pronunciation, focus on clarity, correct stress, and intonation.")
        
        comprehensive_feedback = "\n".join(comprehensive_feedback_parts)

        # --- 6. Logging Final Scores ---
        logger.info(
            f"SummarizeGroupDiscussion Evaluation: Final Evaluation (PTE Scaled): Overall={pte_overall_score:.2f} "
            f"(Content: {pte_content_score:.2f}, Oral Fluency: {pte_oral_fluency_score:.2f}, Pronunciation: {pte_pronunciation_score:.2f})"
        )

        # --- 7. Return Final Result Dictionary ---
        return {
            "scores": {
                "content": pte_content_score,
                "oral_fluency": pte_oral_fluency_score,
                "pronunciation": pte_pronunciation_score,
            },
            "overall_score": pte_overall_score, 
            "feedback": comprehensive_feedback,
            "audio_transcript": audio_transcript, 
        }

    # --- Transcribe Audio (This method is correctly defined here) ---
    def _transcribe_audio_whisper(self, audio_file_stream: bytes) -> tuple[str, List[Dict]]:
        """
        Transcribes audio using local OpenAI Whisper model from a byte stream.
        It saves the stream to a temporary file for Whisper to process.
        """
        if not self.whisper_model:
            logger.warning("Local Whisper model not loaded. Skipping transcription.")
            return "", []

        logger.info("Transcribing audio with Whisper from byte stream.")
        
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_file_stream)
            
            temp_file_path = temp_file.name
            
            result = self.whisper_model.transcribe(temp_file_path, word_timestamps=True)
            
            full_transcript = result.get("text", "").strip()
            words_details = []

            if "segments" in result:
                for segment in result["segments"]:
                    if "words" in segment:
                        for word_data in segment["words"]:
                            words_details.append({
                                "word": word_data["word"].strip(),
                                "start_time": word_data["start"],
                                "end_time": word_data["end"],
                                "confidence": word_data.get("probability", 1.0),
                            })
            
            logger.info(f"Whisper transcription complete. Length: {len(full_transcript)} chars, Words: {len(words_details)}")
            return full_transcript, words_details
        except Exception as e:
            logger.error(f"Local Whisper transcription failed from stream: {e}", exc_info=True)
            raise RuntimeError(f"Whisper transcription error: {e}")
        finally:
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)
                logger.debug(f"Removed temporary audio file: {temp_file.name}")

    def _evaluate_fluency(self, words_details: List[Dict]) -> Tuple[int, str]:
        if not words_details:
            return 0, "No speech detected for fluency evaluation."
        
        total_speaking_duration = 0
        if words_details:
            total_speaking_duration = words_details[-1]["end_time"] - words_details[0]["start_time"]
        
        wpm = (len(words_details) / total_speaking_duration) * 60 if total_speaking_duration > 0 else 0

        pauses = []
        for i in range(1, len(words_details)):
            pause = words_details[i]["start_time"] - words_details[i - 1]["end_time"]
            if pause > 0.5: 
                pauses.append(pause)
        
        avg_pause = statistics.mean(pauses) if pauses else 0

        fluency_score = 5 
        feedback_parts = []

        # WPM scoring
        if wpm < 100:
            fluency_score -= 1
            feedback_parts.append("Speaking rate is a bit slow (below 100 WPM).")
        elif wpm > 180:
            fluency_score -= 1
            feedback_parts.append("Speaking rate is too fast (above 180 WPM).")
        else:
            feedback_parts.append("Speaking rate is appropriate (100-180 WPM).")

        # Pause scoring
        if avg_pause > 1.0:
            fluency_score -= 2
            feedback_parts.append("Frequent long pauses detected (avg > 1.0s), affecting smoothness.")
        elif avg_pause > 0.5:
            fluency_score -= 1
            feedback_parts.append("Some pauses detected (avg > 0.5s), could improve flow.")
        else:
            feedback_parts.append("Minimal pauses, good flow.")

        fluency_score = max(0, min(5, fluency_score)) 

        info_string = f"WPM={int(wpm)}, Avg Pause={round(avg_pause,2)}s. {' '.join(feedback_parts)}"
        return fluency_score, info_string


    def _evaluate_pronunciation(self, words_details: List[Dict]) -> Tuple[int, str]:
        if not words_details:
            return 0, "No speech detected for pronunciation evaluation."
        
        confidences = [w["confidence"] for w in words_details if w.get("confidence", 0) > 0]
        avg_conf = statistics.mean(confidences) if confidences else 0

        if avg_conf >= 0.9:
            score = 5
            feedback = "Excellent clarity and intelligibility."
        elif avg_conf >= 0.8:
            score = 4
            feedback = "Good clarity, generally easy to understand."
        elif avg_conf >= 0.7:
            score = 3
            feedback = "Fair clarity, some words might be unclear."
        elif avg_conf >= 0.6:
            score = 2
            feedback = "Limited clarity, noticeable difficulty in understanding."
        else:
            score = 1
            feedback = "Very low clarity, difficult to understand."

        score = max(0, min(5, score)) 
        info_string = f"Avg confidence={round(avg_conf,2)}. {feedback}"
        return score, info_string

    def _get_llm_content_score_internal(self,
        discussion_data: List[Dict],
        user_summary_text: str,
        topic: Optional[str],
        provider: str = "openai" 
    ) -> Dict[str, Union[float, str]]: # Return a float for pte_content_score
        
        discussion_text = "\n".join([f"{d['speaker']}: {d['text']}" for d in discussion_data])
        
        # [MODIFIED]: Removed the explicit JSON format example from the user prompt.
        # BaseEvaluator will now inject a strict JSON schema into the system message.
        prompt_instruction = f"""
You are a PTE Academic evaluator.
Task: Score the user's summary of a group discussion for CONTENT.

Topic: {topic if topic else 'N/A'}

Original Discussion Transcript:
{discussion_text}

User's Summary (transcribed from audio):
{user_summary_text}

Score each of these aspects on a scale of 0–6, where 0 is completely deficient and 6 is excellent.
- content_score: Does the summary accurately identify and cover all main ideas from the discussion?
- feedback: "<short and specific feedback for content improvement>"
"""
        logger.debug(f"SummarizeGroupDiscussion Content LLM Prompt (truncated): {prompt_instruction[:self.max_input_length]}")
        
        # [MODIFIED]: Define score_key_map and overall_score_key to ensure 'content' is correctly extracted.
        score_key_map = {
            "content": {"key": "scores.content_score", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']}
        }
        # The LLM is only providing "content_score", so we will use it for overall for this internal call.
        overall_score_key = {"key": "overall_score", "llm_output_max_scale": self.trait_definitions['content']['llm_output_max_scale']} 

        if provider != "openai":
            logger.warning(f"SummarizeGroupDiscussion: LLM Provider '{provider}' requested, but BaseEvaluator defaults to OpenAI API. Falling back to OpenAI call.")

        # [MODIFIED]: Pass the correct instruction and mapping to _get_openai_score.
        # This will return a dictionary with PTE-scaled scores and feedback.
        processed_llm_output = self._get_openai_score(
            instruction=prompt_instruction,
            score_key_map=score_key_map,
            overall_score_key=overall_score_key, # LLM outputting content_score and overall_score matching this scale
            default_llm_output_max_scale=self.trait_definitions['content']['llm_output_max_scale'], # Fallback default
            default_feedback_message="" 
        )

        # [MODIFIED]: Directly return the PTE-scaled content score and feedback.
        # No need for reverse scaling or re-scaling, as _get_openai_score handles 0-X to 10-90.
        pte_content_score = processed_llm_output.get("overall_score", 10.0) # overall_score is the PTE-scaled content score
        llm_content_feedback = processed_llm_output.get("feedback", "").strip()

        if not llm_content_feedback:
            llm_content_feedback = "The AI model did not generate specific descriptive feedback for content."
        
        return {
            "pte_content_score": pte_content_score, 
            "content_feedback": llm_content_feedback 
        }