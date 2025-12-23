"""Proofreader module for transcript editing via OpenRouter LLM.

This module handles proofreading of transcripts using Claude 3.5 Sonnet
or other LLMs via the OpenRouter API.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

import requests

logger = logging.getLogger(__name__)

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Available models
AVAILABLE_MODELS = {
    "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-3-haiku": "anthropic/claude-3-haiku",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct",
}

DEFAULT_MODEL = "claude-3.5-sonnet"

# Chunking settings
MAX_CHUNK_CHARS = 25000  # ~6K tokens per chunk, safe for all models
CHUNK_OVERLAP_CHARS = 500  # Overlap to maintain context between chunks

# System prompt for proofreading (loaded from file or default)
DEFAULT_SYSTEM_PROMPT = """You are an expert linguistic editor and transcript specialist. Your task is to process YouTube video transcripts with precision.

## Instructions

1. **Spelling & Grammar Correction**: Fix all spelling errors, typos, grammatical inconsistencies, homophone confusion, punctuation, and capitalization issues.

2. **Transcript Normalization**: Convert raw transcribed text into properly formatted, readable content. Remove filler words (um, uh, you know) unless contextually significant. Add appropriate paragraph breaks. Fix run-on sentences while preserving meaning.

3. **Content Optimization**: Remove sponsor segments, unrelated tangents, technical difficulties mentioned, and administrative announcements. Preserve content that adds context or value.

4. **Output Format**: Return ONLY the edited transcript in Markdown format. Do not include any commentary, explanations, or the summary in the output.

After the edited transcript, on a new line, add exactly this format for the summary (this will be extracted separately):
---SUMMARY---
- Corrected [X] spelling/grammar errors
- Removed [X] filler words
- Deleted [X] unrelated segments
- Retained [X]% of original content
"""


class Proofreader:
    """Handles transcript proofreading via OpenRouter LLM API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        system_prompt_path: Optional[Path] = None
    ):
        """Initialize proofreader.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier (e.g., 'claude-3.5-sonnet')
            system_prompt_path: Path to custom system prompt file
        """
        self._api_key = api_key
        self._model = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS[DEFAULT_MODEL])
        self._model_name = model
        self._system_prompt = self._load_system_prompt(system_prompt_path)
    
    def _load_system_prompt(self, prompt_path: Optional[Path] = None) -> str:
        """Load system prompt from file or use default.
        
        Args:
            prompt_path: Path to prompt file
            
        Returns:
            System prompt string
        """
        if prompt_path and prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                logger.info(f"Loaded custom system prompt from {prompt_path}")
                return content
            except Exception as e:
                logger.warning(f"Could not load prompt file: {e}")
        
        return DEFAULT_SYSTEM_PROMPT
    
    def set_api_key(self, api_key: str) -> None:
        """Set the OpenRouter API key."""
        self._api_key = api_key
    
    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)
    
    def set_model(self, model: str) -> None:
        """Set the model to use.
        
        Args:
            model: Model identifier
        """
        if model in AVAILABLE_MODELS:
            self._model = AVAILABLE_MODELS[model]
            self._model_name = model
            logger.info(f"Proofreader model set to: {model}")
    
    def get_model(self) -> str:
        """Get current model name."""
        return self._model_name
    
    @staticmethod
    def get_available_models() -> list[str]:
        """Get list of available model names."""
        return list(AVAILABLE_MODELS.keys())
    
    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text into chunks, respecting line boundaries.
        
        Args:
            text: Full transcript text
            
        Returns:
            List of text chunks
        """
        if len(text) <= MAX_CHUNK_CHARS:
            return [text]
        
        chunks = []
        # Split by lines (handles both \n and \r\n)
        lines = text.splitlines()
        current_chunk = ""
        
        for line in lines:
            # If adding this line exceeds limit, save current chunk
            if len(current_chunk) + len(line) + 1 > MAX_CHUNK_CHARS and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk (no overlap needed for line-based splitting)
                current_chunk = line
            else:
                current_chunk += ("\n" if current_chunk else "") + line
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If we still only have 1 chunk (very long lines), force split by character
        if len(chunks) == 1 and len(text) > MAX_CHUNK_CHARS:
            chunks = []
            for i in range(0, len(text), MAX_CHUNK_CHARS - CHUNK_OVERLAP_CHARS):
                chunk = text[i:i + MAX_CHUNK_CHARS]
                chunks.append(chunk)
            logger.info(f"Force-split transcript into {len(chunks)} chunks (no line breaks found)")
        else:
            logger.info(f"Split transcript into {len(chunks)} chunks")
        
        return chunks
    
    def _proofread_single(
        self,
        text: str,
        video_title: Optional[str] = None,
        chunk_info: Optional[str] = None
    ) -> dict:
        """Proofread a single chunk of text.
        
        Args:
            text: Text to proofread
            video_title: Optional video title
            chunk_info: Optional chunk info like "chunk 2/5"
            
        Returns:
            dict with edited_text, summary, or error
        """
        # Build the user message
        user_message = f"Please proofread and edit the following transcript"
        if video_title:
            user_message += f" from the video '{video_title}'"
        if chunk_info:
            user_message += f" ({chunk_info})"
        user_message += ".\n\n"
        user_message += "IMPORTANT: You MUST output the COMPLETE edited text in full. Do NOT use placeholders or abbreviate. Write out every paragraph with your corrections applied.\n\n"
        user_message += f"TRANSCRIPT TO EDIT:\n\n{text}"
        
        # Calculate max tokens - estimate output similar to input size
        max_tokens = min(max(len(text) // 3, 8000), 16000)
        
        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/369Temetnosce/yt-dlp-gui",
                    "X-Title": "yt-dlp GUI Proofreader"
                },
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": self._system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content:
                    return {"error": "Empty response from LLM"}
                
                edited_text, summary = self._parse_response(content)
                return {
                    "edited_text": edited_text,
                    "summary": summary,
                    "model": self._model_name
                }
            
            elif response.status_code == 401:
                return {"error": "Invalid OpenRouter API key."}
            elif response.status_code == 429:
                return {"error": "Rate limit exceeded. Please wait and try again."}
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                return {"error": f"OpenRouter API error: {error_msg}"}
                
        except requests.Timeout:
            return {"error": "Request timed out."}
        except Exception as e:
            logger.exception(f"Proofreading error: {e}")
            return {"error": f"Proofreading failed: {str(e)}"}
    
    def proofread(
        self,
        text: str,
        video_title: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Proofread a transcript, automatically chunking if needed.
        
        Args:
            text: Transcript text to proofread
            video_title: Optional video title for context
            progress_callback: Optional callback for progress updates
            
        Returns:
            dict with keys:
            - edited_text: Proofread text in Markdown
            - summary: Summary of changes made
            - error: Error message (only if failed)
        """
        if not self._api_key:
            return {"error": "No OpenRouter API key configured. Please add your API key in Settings."}
        
        if not text.strip():
            return {"error": "No text provided for proofreading."}
        
        # Split into chunks if needed
        chunks = self._split_into_chunks(text)
        total_chunks = len(chunks)
        
        if total_chunks == 1:
            # Single chunk - process directly
            if progress_callback:
                progress_callback(f"Sending to {self._model_name}...")
            return self._proofread_single(text, video_title)
        
        # Multiple chunks - process each
        if progress_callback:
            progress_callback(f"Large transcript: splitting into {total_chunks} chunks...")
        
        all_edited = []
        all_summaries = []
        
        for i, chunk in enumerate(chunks, 1):
            if progress_callback:
                progress_callback(f"Proofreading chunk {i}/{total_chunks}...")
            
            result = self._proofread_single(
                chunk, 
                video_title, 
                chunk_info=f"part {i} of {total_chunks}"
            )
            
            if "error" in result:
                return {"error": f"Failed on chunk {i}/{total_chunks}: {result['error']}"}
            
            all_edited.append(result.get("edited_text", ""))
            if result.get("summary"):
                all_summaries.append(f"Chunk {i}: {result['summary']}")
            
            logger.info(f"Chunk {i}/{total_chunks} proofread successfully")
        
        # Combine results
        combined_text = "\n\n".join(all_edited)
        combined_summary = f"Processed {total_chunks} chunks.\n" + "\n".join(all_summaries[:3])
        if len(all_summaries) > 3:
            combined_summary += f"\n... and {len(all_summaries) - 3} more chunks"
        
        if progress_callback:
            progress_callback("Proofreading complete!")
        
        return {
            "edited_text": combined_text,
            "summary": combined_summary,
            "model": self._model_name,
            "chunks": total_chunks
        }
    
    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse LLM response to extract edited text and summary.
        
        Args:
            content: Raw LLM response
            
        Returns:
            Tuple of (edited_text, summary)
        """
        # Check if response contains the summary separator
        if "---SUMMARY---" in content:
            parts = content.split("---SUMMARY---", 1)
            edited_text = parts[0].strip()
            summary = parts[1].strip() if len(parts) > 1 else "No summary provided"
        else:
            # No separator found, treat entire response as edited text
            edited_text = content.strip()
            summary = "Proofreading complete (no detailed summary available)"
        
        return edited_text, summary
    
    def proofread_file(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Proofread a transcript file.
        
        Args:
            file_path: Path to the transcript file
            progress_callback: Optional callback for progress updates
            
        Returns:
            dict with keys:
            - edited_text: Proofread text
            - summary: Summary of changes
            - output_path: Path to saved edited file
            - error: Error message (only if failed)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        if progress_callback:
            progress_callback(f"Reading {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Extract video title from filename
        video_title = file_path.stem
        
        # Proofread the text
        result = self.proofread(text, video_title, progress_callback)
        
        if "error" in result:
            return result
        
        # Save the edited file
        output_path = file_path.with_name(f"{file_path.stem}-Edited.md")
        
        try:
            # Add header to the edited file
            header = f"# {video_title}\n\n*Edited: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            full_content = header + result["edited_text"]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            result["output_path"] = str(output_path)
            logger.info(f"Saved edited transcript to {output_path}")
            
        except Exception as e:
            logger.error(f"Could not save edited file: {e}")
            result["error"] = f"Proofreading succeeded but could not save file: {e}"
        
        return result
    
    def proofread_files(
        self,
        file_paths: list[str],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> list[dict]:
        """Proofread multiple transcript files.
        
        Args:
            file_paths: List of paths to transcript files
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of result dicts, one per file
        """
        results = []
        total = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            if progress_callback:
                progress_callback(f"Processing file {i}/{total}: {Path(file_path).name}")
            
            result = self.proofread_file(file_path, progress_callback)
            result["source_file"] = file_path
            results.append(result)
            
            # Log progress
            if "error" in result:
                logger.error(f"Failed to proofread {file_path}: {result['error']}")
            else:
                logger.info(f"Proofread {i}/{total}: {file_path}")
        
        return results
    
    def save_edited_transcript(
        self,
        edited_text: str,
        original_path: str,
        video_title: Optional[str] = None
    ) -> Optional[str]:
        """Save edited transcript to file.
        
        Args:
            edited_text: The edited transcript text
            original_path: Path to the original file
            video_title: Optional video title for header
            
        Returns:
            Path to saved file, or None if failed
        """
        original_path = Path(original_path)
        output_path = original_path.with_name(f"{original_path.stem}-Edited.md")
        
        try:
            title = video_title or original_path.stem
            header = f"# {title}\n\n*Edited: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            full_content = header + edited_text
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Saved edited transcript to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Could not save edited file: {e}")
            return None
