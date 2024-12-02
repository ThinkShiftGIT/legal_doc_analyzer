import os
import logging
import tempfile
from typing import List
from pathlib import Path
from moviepy.editor import VideoFileClip
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import numpy as np

from .audio_processor import AudioProcessor
from ..storage.base import BaseChunk

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Process video files for both audio content and visual information."""
    
    def __init__(self, 
                frame_sample_rate: int = 1,
                confidence_threshold: float = 0.5):
        """Initialize video processor.
        
        Args:
            frame_sample_rate: Number of frames to sample per second
            confidence_threshold: Minimum confidence score for object detection
        """
        self.frame_sample_rate = frame_sample_rate
        self.confidence_threshold = confidence_threshold
        
        # Initialize DETR model for object detection
        self.image_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
        
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")
    
    def process(self, file_path: str) -> List[BaseChunk]:
        """Process a video file and return chunks of transcribed audio and detected objects.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            List of text chunks with metadata including timestamps and detected objects
        """
        try:
            video = VideoFileClip(file_path)
            chunks = []
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract audio and transcribe
                temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")
                video.audio.write_audiofile(temp_audio_path, logger=None)
                
                # Process audio using Whisper
                audio_processor = AudioProcessor()
                audio_chunks = audio_processor.process(temp_audio_path)
                chunks.extend(audio_chunks)
                
                # Process video frames
                frame_chunks = self._process_frames(video)
                chunks.extend(frame_chunks)
            
            video.close()
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing video {file_path}: {str(e)}")
            raise
    
    def _process_frames(self, video: VideoFileClip) -> List[BaseChunk]:
        """Process video frames for object detection.
        
        Args:
            video: VideoFileClip object
            
        Returns:
            List of chunks containing detected objects and their timestamps
        """
        chunks = []
        duration = int(video.duration)
        
        try:
            for t in range(0, duration, self.frame_sample_rate):
                # Extract frame
                frame = video.get_frame(t)
                
                # Convert frame to PIL Image
                image = Image.fromarray(frame)
                
                # Prepare image for model
                inputs = self.image_processor(images=image, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                # Perform object detection
                outputs = self.model(**inputs)
                
                # Convert outputs to probabilities
                probas = outputs.logits.softmax(-1)[0, :, :]
                keep = probas.max(-1).values > self.confidence_threshold
                
                # Convert target sizes
                target_sizes = torch.tensor([image.size[::-1]])
                if torch.cuda.is_available():
                    target_sizes = target_sizes.to("cuda")
                
                # Post-process results
                results = self.image_processor.post_process_object_detection(
                    outputs,
                    threshold=self.confidence_threshold,
                    target_sizes=target_sizes
                )[0]
                
                # Create chunk for detected objects
                if len(results["labels"]) > 0:
                    detected_objects = [
                        f"{self.model.config.id2label[label.item()]} ({score:.2f})"
                        for label, score in zip(results["labels"], results["scores"])
                    ]
                    
                    chunk = BaseChunk(
                        content=f"Detected objects at {t}s: {', '.join(detected_objects)}",
                        metadata={
                            "timestamp": t,
                            "type": "object_detection",
                            "objects": detected_objects
                        }
                    )
                    chunks.append(chunk)
        
        except Exception as e:
            logger.error(f"Error processing video frames: {str(e)}")
            raise
        
        return chunks