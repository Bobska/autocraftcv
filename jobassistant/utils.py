"""
Progress tracking utilities for AutoCraftCV
Handles real-time progress updates for long-running operations
"""

import json
import time
import uuid
from django.core.cache import cache
from django.conf import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Utility class for tracking progress of long-running operations"""
    
    def __init__(self, task_id: Optional[str] = None, total_steps: int = 100):
        self.task_id = task_id or str(uuid.uuid4())
        self.total_steps = total_steps
        self.current_step = 0
        self.status = "Initializing..."
        self.stage = "0/0"
        self.completed = False
        self.error_message = None
        self.additional_data = {}
        self.start_time = time.time()
        
    def update(self, step: int, status: str, stage: Optional[str] = None, error: Optional[str] = None):
        """Update progress information"""
        self.current_step = min(step, self.total_steps)
        self.status = status
        if stage:
            self.stage = stage
        if error:
            self.error_message = error
            self.completed = True
        
        # Calculate progress percentage
        progress = int((self.current_step / self.total_steps) * 100)
        
        # Estimate remaining time
        elapsed_time = time.time() - self.start_time
        if self.current_step > 0:
            estimated_total = elapsed_time * (self.total_steps / self.current_step)
            estimated_remaining = max(0, int(estimated_total - elapsed_time))
        else:
            estimated_remaining = None
        
        # Store progress in cache
        progress_data = {
            'task_id': self.task_id,
            'progress': progress,
            'status': self.status,
            'stage': self.stage,
            'error': self.error_message,
            'completed': self.completed or progress >= 100,
            'elapsed_time': int(elapsed_time),
            'estimated_remaining': estimated_remaining,
            'timestamp': time.time(),
            **self.additional_data  # Include any additional data
        }
        
        # Cache for 30 minutes (extended for longer operations)
        cache.set(f'progress_{self.task_id}', progress_data, timeout=1800)
        
        # Also store in database as backup
        try:
            from .models import ProgressTask
            task, created = ProgressTask.objects.get_or_create(
                task_id=self.task_id,
                defaults={
                    'task_type': 'other',
                    'progress': progress,
                    'status_message': self.status,
                    'stage': self.stage,
                    'error_message': self.error_message,
                    'additional_data': self.additional_data
                }
            )
            if not created:
                task.update_progress(progress, self.status, self.stage)
                if self.error_message:
                    task.mark_failed(self.error_message)
                elif progress >= 100:
                    task.mark_completed(self.status)
        except Exception as e:
            logger.warning(f"Failed to store progress in database: {e}")
        
        return progress_data
    
    def complete(self, status: str = "Complete!", additional_data: Optional[Dict[str, Any]] = None):
        """Mark task as completed with optional additional data"""
        self.completed = True
        self.additional_data = additional_data or {}
        return self.update(self.total_steps, status)
    
    def set_error(self, error_message: str):
        """Mark task as failed with error"""
        self.error_message = error_message
        self.completed = True
        return self.update(self.current_step, f"Error: {error_message}")
    
    @classmethod
    def get_progress(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a task (try cache first, then database)"""
        # Try cache first
        progress_data = cache.get(f'progress_{task_id}')
        if progress_data:
            return progress_data
        
        # Fallback to database
        try:
            from .models import ProgressTask
            task = ProgressTask.objects.get(task_id=task_id)
            progress_data = task.to_dict()
            
            # Restore to cache
            cache.set(f'progress_{task_id}', progress_data, timeout=1800)
            return progress_data
        except Exception as e:
            logger.debug(f"Progress not found in database for task {task_id}: {e}")
            return None
    
    @classmethod
    def cleanup_progress(cls, task_id: str):
        """Remove progress data from cache"""
        cache.delete(f'progress_{task_id}')


class JobScrapingProgress:
    """Predefined progress stages for job scraping"""
    
    STAGES = [
        (5, "Validating URL...", "1/6"),
        (15, "Fetching job page...", "2/6"),
        (35, "Parsing HTML content...", "3/6"),
        (60, "Extracting job details...", "4/6"),
        (80, "Processing requirements...", "5/6"),
        (95, "Structuring data...", "6/6"),
        (100, "Complete!", "6/6")
    ]


class ResumeParsingProgress:
    """Predefined progress stages for resume parsing"""
    
    STAGES = [
        (10, "Uploading file...", "1/6"),
        (25, "Validating file format...", "2/6"),
        (45, "Extracting text content...", "3/6"),
        (65, "Parsing sections...", "4/6"),
        (85, "Structuring data...", "5/6"),
        (95, "Finalizing profile...", "6/6"),
        (100, "Complete!", "6/6")
    ]


class AIGenerationProgress:
    """Predefined progress stages for AI content generation"""
    
    STAGES = [
        (10, "Analyzing job posting...", "1/5"),
        (30, "Processing user profile...", "2/5"),
        (60, "Generating content...", "3/5"),
        (85, "Formatting output...", "4/5"),
        (95, "Finalizing documents...", "5/5"),
        (100, "Complete!", "5/5")
    ]


def simulate_progress_delay(min_delay: float = 0.5, max_delay: float = 2.0):
    """Add realistic delay for progress updates"""
    import random
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
