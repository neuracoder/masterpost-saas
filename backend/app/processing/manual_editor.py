"""
Manual Image Editor for Background Removal Touch-ups
Provides fine-grained editing capabilities for background removal corrections
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw
import uuid
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ManualImageEditor:
    """
    Manual image editor for background removal touch-ups.
    Provides tools for erasing background and restoring product parts.
    """

    def __init__(self, processed_dir: Path):
        self.processed_dir = processed_dir
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour

    def init_session(self, image_path: str, job_id: str = None) -> str:
        """
        Initialize editing session with processed image

        Args:
            image_path: Path to the processed image
            job_id: Optional job ID to associate session with

        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())

        try:
            # Load the processed image
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            # Load image using OpenCV for editing operations
            original = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if original is None:
                raise ValueError(f"Could not load image: {image_path}")

            # If image has alpha channel (RGBA), preserve it
            if original.shape[2] == 4:
                working_copy = original.copy()
            else:
                # Convert to RGBA for transparency support
                working_copy = cv2.cvtColor(original, cv2.COLOR_BGR2BGRA)
                original = cv2.cvtColor(original, cv2.COLOR_BGR2BGRA)

            # Create session
            session_data = {
                'original': original,
                'current': working_copy,
                'history': [working_copy.copy()],
                'history_index': 0,
                'image_path': image_path,
                'job_id': job_id,
                'created_at': time.time(),
                'last_activity': time.time(),
                'width': working_copy.shape[1],
                'height': working_copy.shape[0]
            }

            self.active_sessions[session_id] = session_data

            # Save preview image
            preview_path = self._save_preview(session_id, working_copy)
            session_data['preview_path'] = preview_path

            logger.info(f"Initialized editing session {session_id} for image {image_path}")

            return session_id

        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            raise

    def apply_brush_action(self, session_id: str, action: str, coordinates: List[Tuple[int, int]],
                          brush_size: int = 10) -> Optional[str]:
        """
        Apply brush action (erase or restore) to image

        Args:
            session_id: Session identifier
            action: 'erase' or 'restore'
            coordinates: List of (x, y) coordinates for brush stroke
            brush_size: Size of brush in pixels

        Returns:
            preview_path: Path to updated preview image or None if failed
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None

        try:
            session = self.active_sessions[session_id]
            session['last_activity'] = time.time()

            image = session['current'].copy()
            height, width = image.shape[:2]

            # Create mask for the brush stroke
            mask = np.zeros((height, width), dtype=np.uint8)

            # Draw brush stroke on mask
            if len(coordinates) >= 2:
                # Draw lines between consecutive points for smooth stroke
                for i in range(len(coordinates) - 1):
                    x1, y1 = coordinates[i]
                    x2, y2 = coordinates[i + 1]

                    # Ensure coordinates are within image bounds
                    x1 = max(0, min(width - 1, int(x1)))
                    y1 = max(0, min(height - 1, int(y1)))
                    x2 = max(0, min(width - 1, int(x2)))
                    y2 = max(0, min(height - 1, int(y2)))

                    cv2.line(mask, (x1, y1), (x2, y2), 255, brush_size)
            else:
                # Single point
                x, y = coordinates[0]
                x = max(0, min(width - 1, int(x)))
                y = max(0, min(height - 1, int(y)))
                cv2.circle(mask, (x, y), brush_size // 2, 255, -1)

            # Apply action based on type
            if action == "erase":
                # Make pixels transparent (set alpha to 0)
                image[mask == 255, 3] = 0

            elif action == "restore":
                # Restore from original image
                original_pixels = session['original'][mask == 255]
                image[mask == 255] = original_pixels

            else:
                logger.error(f"Unknown action: {action}")
                return None

            # Update session and add to history
            session['current'] = image

            # Trim history if too long (keep last 20 states)
            if len(session['history']) > 20:
                session['history'] = session['history'][-20:]
                session['history_index'] = min(session['history_index'], 19)

            # Add new state to history
            session['history'].append(image.copy())
            session['history_index'] = len(session['history']) - 1

            # Save preview
            preview_path = self._save_preview(session_id, image)
            session['preview_path'] = preview_path

            logger.info(f"Applied {action} brush action to session {session_id}")

            return preview_path

        except Exception as e:
            logger.error(f"Failed to apply brush action: {e}")
            return None

    def undo(self, session_id: str) -> Optional[str]:
        """
        Undo last action

        Args:
            session_id: Session identifier

        Returns:
            preview_path: Path to reverted preview image or None if failed
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None

        try:
            session = self.active_sessions[session_id]
            session['last_activity'] = time.time()

            if session['history_index'] > 0:
                session['history_index'] -= 1
                session['current'] = session['history'][session['history_index']].copy()

                # Save preview
                preview_path = self._save_preview(session_id, session['current'])
                session['preview_path'] = preview_path

                logger.info(f"Undid action in session {session_id}")
                return preview_path
            else:
                logger.info(f"No more actions to undo in session {session_id}")
                return session.get('preview_path')

        except Exception as e:
            logger.error(f"Failed to undo: {e}")
            return None

    def redo(self, session_id: str) -> Optional[str]:
        """
        Redo last undone action

        Args:
            session_id: Session identifier

        Returns:
            preview_path: Path to updated preview image or None if failed
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None

        try:
            session = self.active_sessions[session_id]
            session['last_activity'] = time.time()

            if session['history_index'] < len(session['history']) - 1:
                session['history_index'] += 1
                session['current'] = session['history'][session['history_index']].copy()

                # Save preview
                preview_path = self._save_preview(session_id, session['current'])
                session['preview_path'] = preview_path

                logger.info(f"Redid action in session {session_id}")
                return preview_path
            else:
                logger.info(f"No more actions to redo in session {session_id}")
                return session.get('preview_path')

        except Exception as e:
            logger.error(f"Failed to redo: {e}")
            return None

    def reset_to_original(self, session_id: str) -> Optional[str]:
        """
        Reset image to original state

        Args:
            session_id: Session identifier

        Returns:
            preview_path: Path to reset preview image or None if failed
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None

        try:
            session = self.active_sessions[session_id]
            session['last_activity'] = time.time()

            # Reset to original
            session['current'] = session['original'].copy()

            # Clear history and add current state
            session['history'] = [session['current'].copy()]
            session['history_index'] = 0

            # Save preview
            preview_path = self._save_preview(session_id, session['current'])
            session['preview_path'] = preview_path

            logger.info(f"Reset session {session_id} to original")
            return preview_path

        except Exception as e:
            logger.error(f"Failed to reset: {e}")
            return None

    def save_edited_image(self, session_id: str, output_path: str = None) -> Optional[str]:
        """
        Save the edited image

        Args:
            session_id: Session identifier
            output_path: Optional custom output path

        Returns:
            saved_path: Path to saved image or None if failed
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None

        try:
            session = self.active_sessions[session_id]
            session['last_activity'] = time.time()

            if output_path is None:
                # Generate output path
                timestamp = int(time.time())
                output_path = str(self.processed_dir / f"edited_{session_id}_{timestamp}.png")

            # Save image
            current_image = session['current']

            # Convert from OpenCV format to PIL for saving
            if current_image.shape[2] == 4:  # RGBA
                # Convert BGRA to RGBA
                rgba_image = cv2.cvtColor(current_image, cv2.COLOR_BGRA2RGBA)
                pil_image = Image.fromarray(rgba_image, 'RGBA')
            else:  # RGB
                rgb_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image, 'RGB')

            pil_image.save(output_path, 'PNG')

            logger.info(f"Saved edited image from session {session_id} to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save edited image: {e}")
            return None

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information

        Args:
            session_id: Session identifier

        Returns:
            session_info: Dictionary with session details or None if not found
        """
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]

        return {
            'session_id': session_id,
            'image_path': session['image_path'],
            'job_id': session.get('job_id'),
            'width': session['width'],
            'height': session['height'],
            'created_at': session['created_at'],
            'last_activity': session['last_activity'],
            'history_length': len(session['history']),
            'history_index': session['history_index'],
            'preview_path': session.get('preview_path'),
            'can_undo': session['history_index'] > 0,
            'can_redo': session['history_index'] < len(session['history']) - 1
        }

    def cleanup_session(self, session_id: str) -> bool:
        """
        Clean up session and temporary files

        Args:
            session_id: Session identifier

        Returns:
            success: True if cleaned up successfully
        """
        if session_id not in self.active_sessions:
            return False

        try:
            session = self.active_sessions[session_id]

            # Remove preview file if exists
            preview_path = session.get('preview_path')
            if preview_path and Path(preview_path).exists():
                Path(preview_path).unlink()

            # Remove session
            del self.active_sessions[session_id]

            logger.info(f"Cleaned up session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
            return False

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions

        Returns:
            cleaned_count: Number of sessions cleaned up
        """
        current_time = time.time()
        expired_sessions = []

        for session_id, session in self.active_sessions.items():
            if current_time - session['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)

        cleaned_count = 0
        for session_id in expired_sessions:
            if self.cleanup_session(session_id):
                cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired sessions")

        return cleaned_count

    def _save_preview(self, session_id: str, image: np.ndarray) -> str:
        """
        Save preview image for session

        Args:
            session_id: Session identifier
            image: Image array to save

        Returns:
            preview_path: Path to saved preview
        """
        try:
            preview_filename = f"preview_{session_id}.png"
            preview_path = str(self.processed_dir / preview_filename)

            # Convert from OpenCV format to PIL for saving
            if image.shape[2] == 4:  # RGBA
                rgba_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
                pil_image = Image.fromarray(rgba_image, 'RGBA')
            else:  # RGB
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image, 'RGB')

            # Resize for preview (max 800px)
            max_size = 800
            if max(pil_image.size) > max_size:
                ratio = max_size / max(pil_image.size)
                new_size = tuple(int(dim * ratio) for dim in pil_image.size)
                pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

            pil_image.save(preview_path, 'PNG')

            return preview_path

        except Exception as e:
            logger.error(f"Failed to save preview: {e}")
            raise