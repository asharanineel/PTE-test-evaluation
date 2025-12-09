# #--- START OF FILE evaluators/base_evaluator.py ---

# import sys
# import os

# # [FIX] Add the project's source directory to the Python path when running directly
# if __name__ == "__main__":
#     sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from abc import ABC, abstractmethod
# from typing import Dict, Any
# from utils.openai_client import get_openai_client
# from config import settings
# import json
# import re
# import time
# import logging
# from datetime import datetime

# # [MODIFIED] Get the logger instance configured in main.py
# # Do NOT configure it again here.
# logger = logging.getLogger(__name__)

# class BaseEvaluator(ABC):
#     def __init__(self):
#         self.client = get_openai_client()
#         self.model_name = settings.OPENAI_MODEL_NAME
#         self.max_retries = 3
#         self.retry_delay = 2  # seconds
#         self.max_input_length = 1500

#     @abstractmethod
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         pass

#     def _sanitize_input(self, text: str) -> str:
#         """Truncate and clean input before sending to the model"""
#         if len(text) > self.max_input_length:
#             logger.warning(f"Truncating input from {len(text)} to {self.max_input_length} characters.")
#             text = text[:self.max_input_length] + "... (truncated)"
#         return text.strip()

#     def _clean_json_string(self, text: str) -> str:
#         """Clean up the JSON string to handle common issues"""
#         json_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
#         if json_match:
#             text = json_match.group(1)
        
#         text = re.sub(r'[\x00-\x1F\x7F]', '', text)
#         text = re.sub(r',\s*}', '}', text)
#         text = re.sub(r',\s*]', ']', text)
#         text = re.sub(r'(\w)"(\w)', r'\1\"\2', text)
#         text = re.sub(r',(\s*[}\]])', r'\1', text)
#         return text.strip()

#     def _validate_scores(self, scores: Dict[str, Any]) -> Dict[str, Any]:
#         """Ensure scores are within 0–90 range"""
#         validated_scores = {}
#         for key, value in scores.items():
#             try:
#                 score = float(value)
#                 validated_scores[key] = max(0, min(90, score))
#             except (ValueError, TypeError):
#                 validated_scores[key] = 0
#                 logger.error(f"Invalid score for {key}: {value}")
#         return validated_scores

#     def _retry_openai_request(self, instruction: str) -> Dict[str, Any]:
#         """Retry the OpenAI API request with exponential backoff"""
#         instruction = self._sanitize_input(instruction)
#         raw_response_text = ""

#         for attempt in range(1, self.max_retries + 1):
#             try:
#                 response = self.client.chat.completions.create(
#                     model=self.model_name,
#                     messages=[
#                         {"role": "system", "content": "You are an expert evaluator. Your response must be in JSON format."},
#                         {"role": "user", "content": instruction}
#                     ],
#                     response_format={"type": "json_object"}
#                 )
#                 raw_response_text = response.choices[0].message.content
#                 logger.info(f"OpenAI raw response (attempt {attempt}): {raw_response_text}")

#                 cleaned_result = self._clean_json_string(raw_response_text)
#                 parsed_result = json.loads(cleaned_result)
                
#                 if "scores" in parsed_result:
#                     parsed_result["scores"] = self._validate_scores(parsed_result["scores"])
                
#                 return parsed_result

#             except json.JSONDecodeError as e:
#                 logger.error(f"JSON decode error on attempt {attempt}: {str(e)}, Raw: {raw_response_text}")
#                 if attempt < self.max_retries:
#                     time.sleep(self.retry_delay * attempt)
#                 else:
#                     return {
#                         "error": f"Failed to parse OpenAI JSON after {self.max_retries} attempts: {str(e)}",
#                         "raw_output": raw_response_text
#                     }

#             except Exception as e:
#                 logger.error(f"OpenAI evaluation failed on attempt {attempt}: {str(e)}")
#                 logger.error({
#                     "timestamp": datetime.now().isoformat(),
#                     "instruction": "--- INSTRUCTION HIDDEN FOR BREVITY ---",
#                     "error": str(e),
#                     "raw_output": raw_response_text
#                 })
#                 if attempt < self.max_retries:
#                     time.sleep(self.retry_delay * attempt)
#                 else:
#                     return {
#                         "error": f"OpenAI evaluation failed after {self.max_retries} attempts: {str(e)}",
#                         "raw_output": raw_response_text
#                     }

#     def _fallback_evaluate(self) -> Dict[str, Any]:
#         """Fallback that avoids fake scores or feedback."""
#         return {
#             "error": "OpenAI evaluation failed after multiple attempts. Please try again later.",
#             "warning": "No fallback scoring applied."
#         }

#     def _get_openai_score(self, instruction: str) -> Dict[str, Any]:
#         """
#         Gets a score from the configured OpenAI model.
#         """
#         openai_result = self._retry_openai_request(instruction)

#         if "error" in openai_result:
#             logger.warning("OpenAI model unavailable — using fallback.")
#             return self._fallback_evaluate()
#         return openai_result
# #--- END OF FILE evaluators/base_evaluator.py ---




# import sys
# import os
# from abc import ABC, abstractmethod
# from typing import Dict, Any, Union, List, Optional
# from utils.openai_client import get_openai_client
# from config import settings
# import json
# import re
# import time
# import logging
# from datetime import datetime

# logger = logging.getLogger(__name__)

# class BaseEvaluator(ABC):
#     def __init__(self):
#         self.client = get_openai_client()
#         self.model_name = settings.OPENAI_MODEL_NAME
#         self.max_retries = 3
#         self.retry_delay = 2  # seconds
#         self.max_input_length = 2000 

#     @abstractmethod
#     def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
#         """
#         Abstract method for evaluating a user response.
#         Each specific evaluator must implement this to define its task-specific logic.
#         The implementation should typically call `self._get_openai_score`
#         and then return a dictionary containing 'scores', 'overall_score', and 'feedback'.
#         """
#         pass

#     def _sanitize_input(self, text: str) -> str:
#         """Truncate and clean input before sending to the model."""
#         if len(text) > self.max_input_length:
#             logger.warning(f"Truncating input from {len(text)} to {self.max_input_length} characters. "
#                            f"Consider reviewing the prompt template for this task to make it more concise.")
#             text = text[:self.max_input_length] + "... (truncated)"
#         return text.strip()

#     def _clean_json_string(self, text: str) -> str:
#         """Clean up the JSON string to handle common issues returned by LLMs."""
#         json_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
#         if json_match:
#             text = json_match.group(1)
        
#         text = re.sub(r'[\x00-\x1F\x7F]', '', text) # Remove invalid control characters
#         text = re.sub(r',\s*}', '}', text) # Remove trailing commas before }
#         text = re.sub(r',\s*]', ']', text) # Remove trailing commas before ]
#         text = re.sub(r',(\s*[}\]]\s*)$', r'\1', text) # Remove trailing commas at the end of dict/list
#         return text.strip()

#     def _validate_score_value(self, value: Any, llm_output_max_scale: int = 90) -> float:
#         """
#         Validates, normalizes a single score value to a 10-90 PTE range.
#         Scores below 10 are clamped to 10. Scores above 90 are clamped to 90.
        
#         Args:
#             value: The raw score value from the LLM (can be int, float, or string).
#             llm_output_max_scale: The maximum scale the LLM originally used (e.g., 5 for 0-5 scale, 90 for 0-90).
#         Returns:
#             The validated and normalized score as a float (10-90 range).
#         """
#         raw_numeric_score = 0.0
#         try:
#             raw_numeric_score = float(value)
#         except (ValueError, TypeError):
#             if isinstance(value, str):
#                 lower_value = value.lower().strip()
#                 if lower_value in ["excellent", "perfect", "exemplary", "outstanding"]:
#                     raw_numeric_score = 90.0
#                 elif lower_value in ["very good"]:
#                     raw_numeric_score = 80.0
#                 elif lower_value == "good":
#                     raw_numeric_score = 70.0
#                 elif lower_value == "average" or lower_value == "fair":
#                     raw_numeric_score = 50.0
#                 elif lower_value in ["poor", "weak", "deficient", "unacceptable"]:
#                     raw_numeric_score = 5.0
#                 elif lower_value.endswith("%"):
#                     try:
#                         raw_numeric_score = float(lower_value.replace("%", "").strip())
#                     except (ValueError, TypeError):
#                         pass
#                 else:
#                     try:
#                         numeric_part = re.sub(r'[^\d.]', '', value.strip())
#                         if numeric_part:
#                             raw_numeric_score = float(numeric_part)
#                     except (ValueError, TypeError):
#                         pass
        
#         normalized_score = raw_numeric_score
#         if llm_output_max_scale != 90 and llm_output_max_scale > 0:
#             if raw_numeric_score >= 0 and raw_numeric_score <= llm_output_max_scale:
#                 normalized_score = (raw_numeric_score / llm_output_max_scale) * 90.0
#             elif raw_numeric_score > llm_output_max_scale: # If LLM gives score above its defined max, cap at 90.
#                 normalized_score = 90.0

#         final_score = max(10.0, min(90.0, round(normalized_score)))
        
#         # Log if original numeric score was significantly different from final score
#         if (abs(raw_numeric_score - final_score) > 0.1 and llm_output_max_scale == 90) or \
#            (llm_output_max_scale != 90 and abs(normalized_score - final_score) > 0.1) or \
#            (raw_numeric_score == 0 and value != 0 and value != '0'): # Log if a 0 was parsed from non-zero input
            
#             is_simple_numeric_string = isinstance(value, str) and value.replace('.', '', 1).isdigit()
            
#             if raw_numeric_score == 0 and value != 0 and value != '0' and not is_simple_numeric_string:
#                 logger.warning(f"Unparseable score '{value}' resulted in {final_score}. Please check LLM prompt/output.")
#             elif raw_numeric_score < 10 and raw_numeric_score > 0 and llm_output_max_scale == 90: # Only for 0-90 scale raw scores
#                 logger.debug(f"LLM returned a low score (raw: {raw_numeric_score:.2f}), clamped to PTE minimum {final_score}.")
#             elif raw_numeric_score > 90 and llm_output_max_scale == 90: # Only for 0-90 scale raw scores
#                 logger.debug(f"LLM returned a high score (raw: {raw_numeric_score:.2f}), clamped to PTE maximum {final_score}.")
#             elif llm_output_max_scale != 90: # For scores that underwent scaling
#                 logger.debug(f"Score '{value}' (raw: {raw_numeric_score:.2f}, scale: {llm_output_max_scale}) normalized to {normalized_score:.2f} and clamped to {final_score}.")

#         return final_score

#     # Helper to get nested value from a dictionary using dot notation (now a class method)
#     def _get_nested_value(self, d: Dict, key_path: str): # <-- Now a method of the class
#         parts = key_path.split('.')
#         current = d
#         for part in parts:
#             if isinstance(current, dict) and part in current:
#                 current = current[part]
#             else:
#                 return None
#         return current

#     # --- FIX: _normalize_llm_output_structure now takes full score_key_map and overall_score_key ---
#     def _normalize_llm_output_structure(self, raw_llm_output: Dict[str, Any], score_key_map: Dict[str, Union[str, Dict[str, Any]]], overall_score_key: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         Attempts to normalize the LLM's raw output structure to a consistent format:
#         {'scores': {<sub_score_key>: <value>}, 'overall_score': <value>, 'feedback': '<string>'}
#         This robustly handles cases where the LLM flattens the 'scores' dict, nests them, or uses alternative keys for feedback.
#         """
#         normalized_output = {
#             "scores": {},
#             "overall_score": None, 
#             "feedback": ""
#         }
        
#         # Helper to safely get score-like values
#         def _extract_score_value_helper(obj: Any) -> Optional[Union[int, float, str]]:
#             if isinstance(obj, dict) and "score" in obj:
#                 return obj["score"]
#             if isinstance(obj, (int, float, str)):
#                 return obj
#             return None

#         # --- Aggressively collect all potential score and feedback candidates ---
#         # This will be a temporary flat dictionary of all found score-like values,
#         # keyed by their lowercase, simple name.
#         all_found_scores_and_comments = {} 
#         feedback_candidates_raw = []

#         # Function to recursively scan and collect scores/comments
#         def scan_dict_for_scores_and_comments(d: Dict, prefix=""):
#             for k, v in d.items():
#                 current_key_flat = f"{prefix}{k}" if prefix else k
                
#                 # Check for score value
#                 score_val = _extract_score_value_helper(v)
#                 if score_val is not None:
#                     # Store score by its simple lowercase key
#                     all_found_scores_and_comments[k.lower()] = score_val
#                     # Also try to store by path for complex scenarios
#                     all_found_scores_and_comments[current_key_flat.lower()] = score_val
                
#                 # Check for comments/feedback
#                 if isinstance(v, str) and (k.lower() in ["feedback", "overall_feedback", "overall_assessment", "comments", "text_response"]):
#                     feedback_candidates_raw.append(v)
#                 elif isinstance(v, dict) and "comments" in v and isinstance(v["comments"], str):
#                     feedback_candidates_raw.append(v["comments"])
                
#                 # Recurse for nested dictionaries
#                 if isinstance(v, dict):
#                     scan_dict_for_scores_and_comments(v, prefix=f"{current_key_flat}.")

#         scan_dict_for_scores_and_comments(raw_llm_output)


#         # --- 1. Populate 'normalized_output["scores"]' ---
#         # Now, use the score_key_map to precisely pull scores from all_found_scores_and_comments
#         for output_key, config in score_key_map.items():
#             llm_key_path = config.get("key") if isinstance(config, dict) else config
            
#             # Extract the simple key name from the path (e.g., "content" from "scores.content")
#             simple_key_match = re.search(r'\.?([^.]+)$', llm_key_path)
#             simple_key_name = simple_key_match.group(1) if simple_key_match else output_key # Fallback to output_key
            
#             # Try to find the score using the simple_key_name in all_found_scores_and_comments (case-insensitive)
#             # This is the most reliable way after aggressive scanning
#             score_found = None
#             if simple_key_name.lower() in all_found_scores_and_comments:
#                 score_found = all_found_scores_and_comments[simple_key_name.lower()]
#             # Specific handling for 'fluency' in Retell Lecture (if sub-scores were aggregated)
#             elif output_key == "fluency" and "fluency_coherence" in all_found_scores_and_comments: # Example of aggregated fluency
#                 sub_fluency_scores = [v for k,v in all_found_scores_and_comments.items() if k.startswith("fluency_") and isinstance(v, (int, float))]
#                 if sub_fluency_scores: score_found = sum(sub_fluency_scores) / len(sub_fluency_scores)
            
#             if score_found is not None:
#                 normalized_output["scores"][output_key] = score_found

#         # --- 2. Populate 'overall_score' ---
#         overall_llm_key_path = overall_score_key.get("key") if isinstance(overall_score_key, dict) else overall_score_key
        
#         found_overall_score = None
#         # Try to find overall score using its path
#         found_overall_score = _extract_score_value_helper(self._get_nested_value(raw_llm_output, overall_llm_key_path))

#         # Fallback to common overall score keys in all_found_scores_and_comments (case-insensitive)
#         if found_overall_score is None:
#             for key_candidate in ["overall_score", "overall score", "overall_assessment"]:
#                 if key_candidate.lower() in all_found_scores_and_comments:
#                     found_overall_score = all_found_scores_and_comments[key_candidate.lower()]
#                     break
        
#         normalized_output["overall_score"] = found_overall_score

#         # --- 3. Populate 'feedback' ---
#         consolidated_feedback_parts = []
#         # Filter out non-string/empty and ensure uniqueness of raw feedback candidates
#         for f in feedback_candidates_raw:
#             if f and f.strip() not in consolidated_feedback_parts:
#                 consolidated_feedback_parts.append(f.strip())
        
#         final_feedback_str = " ".join(consolidated_feedback_parts).strip()
        
#         # Add recommendations if present
#         recommendations = raw_llm_output.get("recommendations", [])
#         if recommendations and isinstance(recommendations, list) and recommendations:
#             rec_string = "Recommendations: " + " ".join([str(r).strip() for r in recommendations if r and str(r).strip()])
#             if final_feedback_str:
#                 final_feedback_str += "\n\n" + rec_string
#             else:
#                 final_feedback_str = rec_string
        
#         normalized_output["feedback"] = final_feedback_str
        
#         logger.debug(f"Normalized LLM Output: {normalized_output}")
#         return normalized_output


#     def _process_llm_output(self, llm_output: Dict[str, Any], score_key_map: Dict[str, Union[str, Dict[str, Any]]] = None, overall_score_key: Union[str, Dict[str, Any]] = "overall_score", default_llm_output_max_scale: int = 90, default_feedback_message: str = "The AI model did not generate specific descriptive feedback for this response.") -> Dict[str, Any]:
#         """
#         Processes the raw LLM output dictionary into a standardized format with validated scores (0-90 scale).
#         This includes aggregating granular comments into the main feedback string.
#         """
#         # --- FIX: Normalize LLM output structure first ---
#         # _normalize_llm_output_structure now needs the full score_key_map and overall_score_key
#         # to correctly identify and extract values from the raw LLM output.
#         normalized_llm_output = self._normalize_llm_output_structure(llm_output, score_key_map, overall_score_key)
        
#         processed_scores = {}
        
#         # Process individual sub-scores from the normalized 'scores' dict
#         for output_key, config in score_key_map.items(): # Iterate over original score_key_map
#             llm_output_max_scale_for_subscore = default_llm_output_max_scale
#             if isinstance(config, dict) and "llm_output_max_scale" in config:
#                 llm_output_max_scale_for_subscore = config.get("llm_output_max_scale", default_llm_output_max_scale)
            
#             # Now, fetch the score directly from the normalized_llm_output["scores"] using the output_key
#             score_value = normalized_llm_output["scores"].get(output_key) 

#             if score_value is not None:
#                 processed_scores[output_key] = self._validate_score_value(score_value, llm_output_max_scale_for_subscore)
#             else:
#                 logger.warning(f"Score for '{output_key}' not found in normalized 'scores' dict. Defaulting to 10.0.")
#                 processed_scores[output_key] = 10.0

#         # Extract and validate the overall score from normalized_llm_output
#         final_overall_score = 10.0
        
#         overall_llm_output_max_scale = default_llm_output_max_scale
#         # Get max scale for overall score from overall_score_key config if it's a dict
#         if isinstance(overall_score_key, dict) and "llm_output_max_scale" in overall_score_key:
#              overall_llm_output_max_scale = overall_score_key.get("llm_output_max_scale", default_llm_output_max_scale)
#         elif isinstance(overall_score_key, str):
#             # If overall_score_key is a simple string, its max scale is just default_llm_output_max_scale
#             pass

#         current_overall_value = normalized_llm_output.get("overall_score") # Directly get from normalized output

#         if current_overall_value is not None:
#             final_overall_score = self._validate_score_value(current_overall_value, overall_llm_output_max_scale)
#         elif processed_scores: # If no explicit overall, but sub-scores are present, calculate average
#             if all(isinstance(s, (int, float)) for s in processed_scores.values()):
#                 final_overall_score = sum(processed_scores.values()) / len(processed_scores)
#                 final_overall_score = max(10.0, min(90.0, round(final_overall_score)))
#                 logger.debug(f"Overall score derived from average of sub-scores: {final_overall_score}")
#             else:
#                 logger.warning("Skipping overall score averaging due to invalid sub-scores. Defaulting overall to 10.0.")
#         else:
#             logger.warning(f"Could not find explicit overall score in normalized output and no sub-scores available for averaging. Defaulting overall to 10.0.")

#         # Ensure comments/feedback is extracted gracefully from normalized_llm_output
#         final_feedback_string = normalized_llm_output.get("feedback", "").strip()
        
#         # Use the passed default_feedback_message ONLY if NO feedback was aggregated at all.
#         if not final_feedback_string.strip(): # Check if it's empty or only whitespace
#             logger.critical(f"LLM failed to provide any feedback, even after normalization. Using default: '{default_feedback_message}'")
#             final_feedback_string = default_feedback_message


#         return {
#             "scores": processed_scores,
#             "overall_score": final_overall_score,
#             "feedback": final_feedback_string
#         }

#     def _retry_openai_request(self, instruction: str, response_format_type: str = "json_object") -> Dict[str, Any]:
#         """
#         Retry the OpenAI API request with exponential backoff.
#         Returns a dictionary indicating success/failure and the raw LLM output or error feedback.
#         """
#         # Strengthen the system message to explicitly demand feedback in the expected JSON
#         system_message_content = f"You are an expert evaluator. Your response MUST be in {response_format_type} format only, and MUST include an overall 'feedback' string explaining the scores. Ensure all scores are numerical."
#         instruction_sanitized = self._sanitize_input(instruction)
#         raw_response_text = ""

#         for attempt in range(1, self.max_retries + 1):
#             try:
#                 logger.debug(f"Attempting LLM call with model '{self.model_name}', attempt {attempt}.")
#                 response = self.client.chat.completions.create(
#                     model=self.model_name,
#                     messages=[
#                         {"role": "system", "content": system_message_content}, # <-- Using strengthened system message
#                         {"role": "user", "content": instruction_sanitized}
#                     ],
#                     response_format={"type": response_format_type}, # This is important
#                     temperature=0.0 # To encourage consistent output
#                 )
#                 raw_response_text = response.choices[0].message.content
#                 logger.info(f"OpenAI raw response (attempt 1): {raw_response_text}")

#                 if response_format_type == "json_object":
#                     cleaned_result = self._clean_json_string(raw_response_text)
#                     parsed_result = json.loads(cleaned_result)
#                 else: # For plain text responses
#                     parsed_result = {"text_response": raw_response_text}
                
#                 return {
#                     "status": "success",
#                     "llm_output": parsed_result
#                 }

#             except json.JSONDecodeError as e:
#                 logger.error(f"JSON decode error on attempt {attempt}: {str(e)}, Raw: {raw_response_text}", exc_info=True)
#                 if attempt < self.max_retries:
#                     time.sleep(self.retry_delay * attempt)
#                 else:
#                     return {
#                         "status": "failure",
#                         "feedback": f"Failed to parse OpenAI JSON after {self.max_retries} attempts: {str(e)}. Raw: {raw_response_text}",
#                         "raw_output": raw_response_text
#                     }

#             except Exception as e:
#                 logger.error(f"OpenAI API request failed on attempt {attempt}: {str(e)}", exc_info=True)
#                 logger.error({
#                     "timestamp": datetime.now().isoformat(),
#                     "instruction": instruction_sanitized, # Log the sanitized instruction for debugging
#                     "error": str(e),
#                     "raw_output": raw_response_text
#                 })
#                 if attempt < self.max_retries:
#                     time.sleep(self.retry_delay * attempt)
#                 else:
#                     return {
#                         "status": "failure",
#                         "feedback": f"OpenAI evaluation failed after {self.max_retries} attempts: {str(e)}. Raw: {raw_response_text}",
#                         "raw_output": raw_response_text
#                     }
#         # Fallback if loop finishes without returning (shouldn't happen with max_retries)
#         return {
#             "status": "failure",
#             "feedback": "An unexpected error occurred during OpenAI request processing (no response after retries).",
#             "raw_output": ""
#         }

#     def _get_openai_score(self, instruction: str, score_key_map: Dict[str, Union[str, Dict[str, Any]]] = None, overall_score_key: Union[str, Dict[str, Any]] = "overall_score", default_llm_output_max_scale: int = 90, response_format_type: str = "json_object", default_feedback_message: str = "The AI model did not generate specific descriptive feedback for this response.") -> Dict[str, Any]:
#         """
#         Gets a score from the configured OpenAI model and processes it.
#         Returns a standardized dictionary of scores and feedback (all scores 0-90, min 10).
#         """
#         openai_response_wrapper = self._retry_openai_request(instruction, response_format_type)

#         if openai_response_wrapper.get("status") == "failure":
#             feedback = openai_response_wrapper.get("feedback", default_feedback_message)
#             logger.error(f"BaseEvaluator: _get_openai_score returning fallback due to failure status. Feedback: {feedback}")
#             return self._fallback_evaluate(custom_feedback=feedback)
        
#         llm_output = openai_response_wrapper["llm_output"]
        
#         if response_format_type == "json_object":
#             processed_output = self._process_llm_output(llm_output, score_key_map, overall_score_key, default_llm_output_max_scale, default_feedback_message)
#             return processed_output
#         else: # For plain text, return the text directly, without detailed scores, but with overall=10.0
#             return {"scores": {}, "overall_score": 10.0, "feedback": llm_output.get("text_response", default_feedback_message)}


#     def _fallback_evaluate(self, custom_feedback: str = None) -> Dict[str, Any]:
#         """
#         Fallback that returns minimum PTE scores (10.0 for all categories).
#         Used when OpenAI evaluation completely fails.
#         """
#         feedback = custom_feedback if custom_feedback else "An unexpected evaluation error occurred. Returning minimum scores. Please contact support if this persists."
#         logger.warning(f"BaseEvaluator fallback triggered: {feedback}")
        
#         # Prepare a default 'scores' dictionary with 10.0s for common keys.
#         default_scores = {
#             "content": 10.0, "fluency": 10.0, "grammar": 10.0, "vocabulary": 10.0,
#             "pronunciation": 10.0, "intonation": 10.0, "stress": 10.0, "accuracy": 10.0,
#             "relevance": 10.0, "task_achievement": 10.0, "form": 10.0, "spelling_punctuation": 10.0,
#             "development_structure_coherence": 10.0, "conciseness": 10.0, "clarity": 10.0,
#             "coherence_and_cohesion": 10.0, "lexical_resource": 10.0,
#             "grammatical_range_and_accuracy": 10.0 
#         }

#         return {
#             "scores": default_scores,
#             "overall_score": 10.0, # Minimum PTE score
#             "feedback": feedback
#         }


# latest code 
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List, Optional
from utils.openai_client import get_openai_client
from config import settings
import json
import re
import time
import logging
from datetime import datetime
# --- ADDED IMPORTS FOR SPECIFIC OPENAI EXCEPTIONS ---
from openai import APIConnectionError, RateLimitError, APIStatusError

logger = logging.getLogger(__name__)

class BaseEvaluator(ABC):
    def __init__(self):
        self.client = get_openai_client()
        self.model_name = settings.OPENAI_MODEL_NAME
        self.max_retries = 5  # --- MODIFIED: Increased retry attempts ---
        self.retry_delay = 5  # --- MODIFIED: Increased delay between retries ---
        self.max_input_length = 2000 

    @abstractmethod
    def evaluate(self, prompt: str, user_response: str) -> Dict[str, Any]:
        """
        Abstract method for evaluating a user response.
        Each specific evaluator must implement this to define its task-specific logic.
        The implementation should typically call `self._get_openai_score`
        and then return a dictionary containing 'scores', 'overall_score', and 'feedback'.
        """
        pass

    def _sanitize_input(self, text: str) -> str:
        """Truncate and clean input before sending to the model."""
        if len(text) > self.max_input_length:
            logger.warning(f"Truncating input from {len(text)} to {self.max_input_length} characters. "
                           f"Consider reviewing the prompt template for this task to make it more concise.")
            text = text[:self.max_input_length] + "... (truncated)"
        return text.strip()

    def _clean_json_string(self, text: str) -> str:
        """Clean up the JSON string to handle common issues returned by LLMs."""
        json_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        text = re.sub(r'[\x00-\x1F\x7F]', '', text) # Remove invalid control characters
        text = re.sub(r',\s*}', '}', text) # Remove trailing commas before }
        text = re.sub(r',\s*]', ']', text) # Remove trailing commas before ]
        text = re.sub(r',(\s*[}\]]\s*)$', r'\1', text) # Remove trailing commas at the end of dict/list
        return text.strip()

    def _validate_score_value(self, value: Any, llm_output_max_scale: int = 90) -> float:
        """
        Validates, normalizes a single score value to a 10-90 PTE range.
        Scores below 10 are clamped to 10. Scores above 90 are clamped to 90.
        
        Args:
            value: The raw score value from the LLM (can be int, float, or string).
            llm_output_max_scale: The maximum scale the LLM originally used (e.g., 5 for 0-5 scale, 90 for 0-90).
        Returns:
            The validated and normalized score as a float (10-90 range).
        """
        raw_numeric_score = 0.0
        try:
            raw_numeric_score = float(value)
        except (ValueError, TypeError):
            if isinstance(value, str):
                lower_value = value.lower().strip()
                if lower_value in ["excellent", "perfect", "exemplary", "outstanding"]:
                    raw_numeric_score = 90.0
                elif lower_value in ["very good"]:
                    raw_numeric_score = 80.0
                elif lower_value == "good":
                    raw_numeric_score = 70.0
                elif lower_value == "average" or lower_value == "fair":
                    raw_numeric_score = 50.0
                elif lower_value in ["poor", "weak", "deficient", "unacceptable"]:
                    raw_numeric_score = 5.0
                elif lower_value.endswith("%"):
                    try:
                        raw_numeric_score = float(lower_value.replace("%", "").strip())
                    except (ValueError, TypeError):
                        pass
                else:
                    try:
                        numeric_part = re.sub(r'[^\d.]', '', value.strip())
                        if numeric_part:
                            raw_numeric_score = float(numeric_part)
                    except (ValueError, TypeError):
                        pass
        
        normalized_score = raw_numeric_score
        if llm_output_max_scale != 90 and raw_numeric_score > 0: 
            if raw_numeric_score >= 0 and raw_numeric_score <= llm_output_max_scale:
                normalized_score = (raw_numeric_score / llm_output_max_scale) * 90.0
            elif raw_numeric_score > llm_output_max_scale: 
                normalized_score = 90.0
        elif llm_output_max_scale == 0: 
             normalized_score = 0.0

        final_score = max(10.0, min(90.0, round(normalized_score)))
        
        if (abs(raw_numeric_score - final_score) > 0.1 and llm_output_max_scale == 90) or \
           (llm_output_max_scale != 90 and abs(normalized_score - final_score) > 0.1) or \
           (raw_numeric_score == 0 and value != 0 and value != '0'):
            
            is_simple_numeric_string = isinstance(value, str) and value.replace('.', '', 1).isdigit()
            
            if raw_numeric_score == 0 and value != 0 and value != '0' and not is_simple_numeric_string:
                logger.warning(f"Unparseable score '{value}' resulted in {final_score}. Please check LLM prompt/output.")
            elif raw_numeric_score < 10 and raw_numeric_score > 0 and llm_output_max_scale == 90:
                logger.debug(f"LLM returned a low score (raw: {raw_numeric_score:.2f}), clamped to PTE minimum {final_score}.")
            elif raw_numeric_score > 90 and llm_output_max_scale == 90:
                logger.debug(f"LLM returned a high score (raw: {raw_numeric_score:.2f}), clamped to PTE maximum {final_score}.")
            elif llm_output_max_scale != 90:
                logger.debug(f"Score '{value}' (raw: {raw_numeric_score:.2f}, scale: {llm_output_max_scale}) normalized to {normalized_score:.2f} and clamped to {final_score}.")

        return final_score

    def _get_nested_value(self, d: Dict, key_path: str):
        parts = key_path.split('.')
        current = d
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def _normalize_llm_output_structure(self, raw_llm_output: Dict[str, Any], score_key_map: Dict[str, Union[str, Dict[str, Any]]], overall_score_key: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Attempts to normalize the LLM's raw output structure to a consistent format:
        {'scores': {<sub_score_key>: <value>}, 'overall_score': <value>, 'feedback': '<string>'}
        This robustly handles cases where the LLM flattens the 'scores' dict, nests them, or uses alternative keys for feedback.
        """
        normalized_output = {
            "scores": {},
            "overall_score": None, 
            "feedback": ""
        }
        
        def _extract_score_value_helper(obj: Any) -> Optional[Union[int, float, str]]:
            if isinstance(obj, dict) and "score" in obj:
                return obj["score"]
            if isinstance(obj, (int, float, str)):
                return obj
            return None

        all_found_scores_and_comments = {} 
        feedback_candidates_raw = []

        def scan_dict_for_scores_and_comments(d: Dict, prefix=""):
            for k, v in d.items():
                current_key_flat = f"{prefix}{k}" if prefix else k
                
                score_val = _extract_score_value_helper(v)
                if score_val is not None:
                    all_found_scores_and_comments[k.lower()] = score_val
                    all_found_scores_and_comments[current_key_flat.lower()] = score_val
                
                if isinstance(v, str) and (k.lower() in ["feedback", "overall_feedback", "overall_assessment", "comments", "text_response"]):
                    feedback_candidates_raw.append(v)
                elif isinstance(v, dict) and "comments" in v and isinstance(v["comments"], str):
                    feedback_candidates_raw.append(v["comments"])
                
                if isinstance(v, dict):
                    scan_dict_for_scores_and_comments(v, prefix=f"{current_key_flat}.")

        scan_dict_for_scores_and_comments(raw_llm_output)


        # --- 1. Populate 'normalized_output["scores"]' ---
        for output_key, config in score_key_map.items():
            llm_key_path = config.get("key") if isinstance(config, dict) else config
            
            score_found_for_output_key = None
            
            # Primary lookup: Use the full llm_key_path with _get_nested_value from the raw LLM output
            nested_value = self._get_nested_value(raw_llm_output, llm_key_path)
            score_found_for_output_key = _extract_score_value_helper(nested_value)
            
            # Fallback 1: If not found, try searching the flattened `all_found_scores_and_comments` for the simple key name
            if score_found_for_output_key is None:
                simple_key_name = llm_key_path.split('.')[-1]
                if simple_key_name.lower() in all_found_scores_and_comments:
                    score_found_for_output_key = all_found_scores_and_comments[simple_key_name.lower()]
                    logger.debug(f"Fallback 1: Found score for '{output_key}' via simple key '{simple_key_name.lower()}' in flattened map.")

            # Fallback 2: Try searching the flattened `all_found_scores_and_comments` for the full path key
            if score_found_for_output_key is None and llm_key_path.lower() in all_found_scores_and_comments:
                score_found_for_output_key = all_found_scores_and_comments[llm_key_path.lower()]
                logger.debug(f"Fallback 2: Found score for '{output_key}' via full path '{llm_key_path.lower()}' in flattened map.")
            
            # --- NEW: Additional fallback for common LLM deviations (expanded) ---
            if score_found_for_output_key is None:
                # Common deviations for 'content'
                if output_key == "content":
                    if "content_quality" in all_found_scores_and_comments:
                        score_found_for_output_key = all_found_scores_and_comments["content_quality"]
                        logger.debug(f"Fallback 3: Found 'content' via 'content_quality'.")
                    elif "content_coverage" in all_found_scores_and_comments:
                        score_found_for_output_key = all_found_scores_and_comments["content_coverage"]
                        logger.debug(f"Fallback 3: Found 'content' via 'content_coverage'.")
                    elif "clarity_score" in all_found_scores_and_comments:
                         score_found_for_output_key = all_found_scores_and_comments["clarity_score"]
                         logger.debug(f"Fallback 3: Found 'content' via 'clarity_score'.")
                
                # Common deviations for 'development_structure_coherence'
                elif output_key == "development_structure_coherence":
                    if "structure" in all_found_scores_and_comments:
                        score_found_for_output_key = all_found_scores_and_comments["structure"]
                        logger.debug(f"Fallback 3: Found 'development_structure_coherence' via 'structure'.")
                    elif "organization" in all_found_scores_and_comments:
                         score_found_for_output_key = all_found_scores_and_comments["organization"]
                         logger.debug(f"Fallback 3: Found 'development_structure_coherence' via 'organization'.")

                # Common deviations for 'grammar'
                elif output_key == "grammar" and "language_accuracy" in all_found_scores_and_comments:
                    score_found_for_output_key = all_found_scores_and_comments["language_accuracy"]
                    logger.debug(f"Fallback 3: Found 'grammar' via 'language_accuracy'.")
                
                # Common deviations for 'task_achievement'
                elif output_key == "task_achievement" and "argument_development" in all_found_scores_and_comments:
                    score_found_for_output_key = all_found_scores_and_comments["argument_development"]
                    logger.debug(f"Fallback 3: Found 'task_achievement' via 'argument_development'.")
                
                # Common deviations for 'relevance'
                elif output_key == "relevance" and "relevance_score" in all_found_scores_and_comments:
                    score_found_for_output_key = all_found_scores_and_comments["relevance_score"]
                    logger.debug(f"Fallback 3: Found 'relevance' via 'relevance_score'.")

                # Common deviations for 'form' (Summarize Written Text)
                elif output_key == "form" and "conciseness" in all_found_scores_and_comments:
                    score_found_for_output_key = all_found_scores_and_comments["conciseness"]
                    logger.debug(f"Fallback 3: Found 'form' via 'conciseness'.")

            if score_found_for_output_key is not None:
                normalized_output["scores"][output_key] = score_found_for_output_key
            else:
                logger.warning(f"Score for '{output_key}' (path '{llm_key_path}') was not found via direct lookup or flattened candidates. Will be defaulted to 10.0 later.")


        # --- 2. Populate 'overall_score' ---
        overall_llm_key_path = overall_score_key.get("key") if isinstance(overall_score_key, dict) else overall_score_key
        
        found_overall_score = None
        # Primary lookup for overall score: direct nested value
        found_overall_score = _extract_score_value_helper(self._get_nested_value(raw_llm_output, overall_llm_key_path))

        # Fallback to common overall score keys in all_found_scores_and_comments (case-insensitive)
        if found_overall_score is None:
            for key_candidate in ["overall_score", "overall score", "overall_assessment"]:
                if key_candidate.lower() in all_found_scores_and_comments:
                    found_overall_score = all_found_scores_and_comments[key_candidate.lower()]
                    logger.debug(f"Fallback: Found overall score via common key '{key_candidate.lower()}' in flattened map.")
                    break
        
        # --- NEW: If overall_score is still not found and LLM provided content_score/content_quality etc.
        if found_overall_score is None:
             potential_overall_score_candidates = [
                all_found_scores_and_comments.get("overall_score"),
                all_found_scores_and_comments.get("overall score"),
                all_found_scores_and_comments.get("overall_assessment"),
                all_found_scores_and_comments.get("content_score"),
                all_found_scores_and_comments.get("content_quality"),
                all_found_scores_and_comments.get("clarity_score"),
                all_found_scores_and_comments.get("relevance_score"),
             ]
             numeric_candidates = [s for s in potential_overall_score_candidates if isinstance(s, (int, float))]
             if numeric_candidates:
                found_overall_score = max(numeric_candidates) 
                logger.debug(f"Fallback: Derived overall score from highest available numeric candidate: {found_overall_score}")

        normalized_output["overall_score"] = found_overall_score

        # --- 3. Populate 'feedback' ---
        consolidated_feedback_parts = []
        for f in feedback_candidates_raw:
            if f and f.strip() not in consolidated_feedback_parts:
                consolidated_feedback_parts.append(f.strip())
        
        final_feedback_str = " ".join(consolidated_feedback_parts).strip()
        
        recommendations = raw_llm_output.get("recommendations", [])
        if recommendations and isinstance(recommendations, list) and recommendations:
            rec_string = "Recommendations: " + " ".join([str(r).strip() for r in recommendations if r and str(r).strip()])
            if final_feedback_str:
                final_feedback_str += "\n\n" + rec_string
            else:
                final_feedback_str = rec_string
        
        normalized_output["feedback"] = final_feedback_str
        
        logger.debug(f"Normalized LLM Output: {normalized_output}")
        return normalized_output


    def _process_llm_output(self, llm_output: Dict[str, Any], score_key_map: Dict[str, Union[str, Dict[str, Any]]] = None, overall_score_key: Union[str, Dict[str, Any]] = "overall_score", default_llm_output_max_scale: int = 90, default_feedback_message: str = "The AI model did not generate specific descriptive feedback for this response.") -> Dict[str, Any]:
        """
        Processes the raw LLM output dictionary into a standardized format with validated scores (0-90 scale).
        This includes aggregating granular comments into the main feedback string.
        """
        normalized_llm_output = self._normalize_llm_output_structure(llm_output, score_key_map, overall_score_key)
        
        processed_scores = {}
        
        for output_key, config in score_key_map.items():
            llm_output_max_scale_for_subscore = default_llm_output_max_scale
            if isinstance(config, dict) and "llm_output_max_scale" in config:
                llm_output_max_scale_for_subscore = config.get("llm_output_max_scale", default_llm_output_max_scale)
            
            score_value = normalized_llm_output["scores"].get(output_key) 

            if score_value is not None:
                processed_scores[output_key] = self._validate_score_value(score_value, llm_output_max_scale_for_subscore)
            else:
                logger.warning(f"Score for '{output_key}' not found in normalized 'scores' dict. Defaulting to 10.0.")
                processed_scores[output_key] = 10.0

        final_overall_score = 10.0
        
        overall_llm_output_max_scale = default_llm_output_max_scale
        if isinstance(overall_score_key, dict) and "llm_output_max_scale" in overall_score_key:
             overall_llm_output_max_scale = overall_score_key.get("llm_output_max_scale", default_llm_output_max_scale)

        current_overall_value = normalized_llm_output.get("overall_score")

        if current_overall_value is not None:
            final_overall_score = self._validate_score_value(current_overall_value, overall_llm_output_max_scale)
        elif processed_scores:
            if all(isinstance(s, (int, float)) for s in processed_scores.values()):
                final_overall_score = sum(processed_scores.values()) / len(processed_scores)
                final_overall_score = max(10.0, min(90.0, round(final_overall_score)))
                logger.debug(f"Overall score derived from average of sub-scores: {final_overall_score}")
            else:
                logger.warning("Skipping overall score averaging due to invalid sub-scores. Defaulting overall to 10.0.")
        else:
            logger.warning(f"Could not find explicit overall score in normalized output and no sub-scores available for averaging. Defaulting overall to 10.0.")

        final_feedback_string = normalized_llm_output.get("feedback", "").strip()
        
        if not final_feedback_string.strip():
            logger.critical(f"LLM failed to provide any feedback, even after normalization. Using default: '{default_feedback_message}'")
            final_feedback_string = default_feedback_message


        return {
            "scores": processed_scores,
            "overall_score": final_overall_score,
            "feedback": final_feedback_string
        }

    def _retry_openai_request(self, instruction: str, response_format_type: str = "json_object", expected_json_schema_example: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retry the OpenAI API request with exponential backoff.
        Returns a dictionary indicating success/failure and the raw LLM output or error feedback.
        
        Args:
            instruction (str): The user instruction for the LLM.
            response_format_type (str): "json_object" or "text".
            expected_json_schema_example (Optional[Dict[str, Any]]): A JSON example to strictly enforce the output format.
        """
        system_message_content = "You are an expert evaluator. Your response MUST be in JSON format only."
        if expected_json_schema_example:
            system_message_content += f" The JSON structure MUST exactly match this example:\n```json\n{json.dumps(expected_json_schema_example, indent=2)}\n```\nEnsure all scores are numerical, and provide an overall 'feedback' string."
        else:
            system_message_content += " Ensure all scores are numerical, and provide an overall 'feedback' string explaining the scores."
        
        instruction_sanitized = self._sanitize_input(instruction)
        raw_response_text = ""

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Attempting LLM call with model '{self.model_name}', attempt {attempt}.")
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_message_content},
                        {"role": "user", "content": instruction_sanitized}
                    ],
                    response_format={"type": response_format_type},
                    temperature=0.0
                )
                raw_response_text = response.choices[0].message.content
                logger.info(f"OpenAI raw response (attempt {attempt}): {raw_response_text}")

                if response_format_type == "json_object":
                    cleaned_result = self._clean_json_string(raw_response_text)
                    parsed_result = json.loads(cleaned_result)
                else:
                    parsed_result = {"text_response": raw_response_text}
                
                return {
                    "status": "success",
                    "llm_output": parsed_result
                }

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error on attempt {attempt}: {str(e)}, Raw: {raw_response_text}", exc_info=True)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    return {
                        "status": "failure",
                        "feedback": f"Failed to parse OpenAI JSON after {self.max_retries} attempts: {str(e)}. Raw: {raw_response_text}",
                        "raw_output": raw_response_text
                    }
            # --- ADDED: Specific Exception Handlers for OpenAI API errors ---
            except APIConnectionError as e:
                logger.error(f"OpenAI API Connection Error on attempt {attempt}: {e}", exc_info=True)
                logger.critical(f"A definite connection issue detected: {e}. Check network, firewall, or proxy settings.")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    return {
                        "status": "failure",
                        "feedback": f"OpenAI API connection failed after {self.max_retries} attempts: {str(e)}.",
                        "raw_output": raw_response_text
                    }
            except RateLimitError as e:
                logger.warning(f"OpenAI API Rate Limit Error on attempt {attempt}: {e}", exc_info=True)
                logger.warning(f"Rate limit hit. Retrying in {self.retry_delay * attempt} seconds.")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    return {
                        "status": "failure",
                        "feedback": f"OpenAI API rate limit exceeded after {self.max_retries} attempts: {str(e)}.",
                        "raw_output": raw_response_text
                    }
            except APIStatusError as e:
                logger.error(f"OpenAI API Status Error (HTTP {e.status_code}) on attempt {attempt}: {e}", exc_info=True)
                logger.error(f"OpenAI server returned an error: {e.response}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    return {
                        "status": "failure",
                        "feedback": f"OpenAI API server error after {self.max_retries} attempts (Status {e.status_code}): {str(e)}.",
                        "raw_output": e.response.text if e.response else "No response text provided by API"
                    }
            # --- END ADDED EXCEPTION BLOCKS ---
            except Exception as e: # This generic catch is now the last in the chain
                logger.error(f"OpenAI API request failed (generic error) on attempt {attempt}: {str(e)}", exc_info=True)
                logger.error({
                    "timestamp": datetime.now().isoformat(),
                    "instruction_prefix": instruction_sanitized[:500], # --- MODIFIED: Log prefix for brevity ---
                    "error": str(e),
                    "raw_output": raw_response_text
                })
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    return {
                        "status": "failure",
                        "feedback": f"OpenAI evaluation failed after {self.max_retries} attempts: {str(e)}. Raw: {raw_response_text}",
                        "raw_output": raw_response_text
                    }
        return {
            "status": "failure",
            "feedback": "An unexpected error occurred during OpenAI request processing (no response after retries).",
            "raw_output": ""
        }

    def _get_openai_score(self, instruction: str, score_key_map: Dict[str, Union[str, Dict[str, Any]]] = None, overall_score_key: Union[str, Dict[str, Any]] = "overall_score", default_llm_output_max_scale: int = 90, response_format_type: str = "json_object", default_feedback_message: str = "The AI model did not generate specific descriptive feedback for this response.") -> Dict[str, Any]:
        """
        Gets a score from the configured OpenAI model and processes it.
        Returns a standardized dictionary of scores and feedback (all scores 0-90, min 10).
        """
        expected_schema_example = {
            "scores": {k: "<number>" for k in score_key_map.keys()},
            "overall_score": "<number>",
            "feedback": "<string>"
        }

        openai_response_wrapper = self._retry_openai_request(instruction, response_format_type, expected_schema_example) # --- CONFIRMED: `expected_schema_example` is correctly used ---

        if openai_response_wrapper.get("status") == "failure":
            feedback = openai_response_wrapper.get("feedback", default_feedback_message)
            logger.error(f"BaseEvaluator: _get_openai_score returning fallback due to failure status. Feedback: {feedback}")
            return self._fallback_evaluate(custom_feedback=feedback)
        
        llm_output = openai_response_wrapper["llm_output"]
        
        if response_format_type == "json_object":
            processed_output = self._process_llm_output(llm_output, score_key_map, overall_score_key, default_llm_output_max_scale, default_feedback_message)
            return processed_output
        else:
            return {"scores": {}, "overall_score": 10.0, "feedback": llm_output.get("text_response", default_feedback_message)}
            
    def _fallback_evaluate(self, custom_feedback: str = None) -> Dict[str, Any]:
        """
        Fallback that returns minimum PTE scores (10.0 for all categories).
        Used when OpenAI evaluation completely fails.
        """
        feedback = custom_feedback if custom_feedback else "An unexpected evaluation error occurred. Returning minimum scores. Please contact support if this persists."
        logger.warning(f"BaseEvaluator fallback triggered: {feedback}")
        
        default_scores = {
            "content": 10.0, "fluency": 10.0, "grammar": 10.0, "vocabulary": 10.0,
            "pronunciation": 10.0, "intonation": 10.0, "stress": 10.0, "accuracy": 10.0,
            "relevance": 10.0, "task_achievement": 10.0, "form": 10.0, "spelling_punctuation": 10.0,
            "development_structure_coherence": 10.0, "conciseness": 10.0, "clarity": 10.0,
            "coherence_and_cohesion": 10.0, "lexical_resource": 10.0,
            "grammatical_range_and_accuracy": 10.0 
        }

        return {
            "scores": default_scores,
            "overall_score": 10.0,
            "feedback": feedback
        }