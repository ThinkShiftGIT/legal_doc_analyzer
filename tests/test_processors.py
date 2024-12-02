import pytest
from pathlib import Path
import sys
from legal_doc_analyzer.processors.audio_processor import AudioProcessor
from legal_doc_analyzer.processors.video_processor import VideoProcessor
from legal_doc_analyzer.processors.pdf_processor import PDFProcessor
from legal_doc_analyzer.storage.vector_store import ChromaStore

# Add tests directory to Python path
test_dir = Path(__file__).parent
sys.path.append(str(test_dir))

from create_test_data import create_test_audio, create_test_video, create_test_pdf

# Test data directory
TEST_DIR = Path(__file__).parent / "test_data"

def test_pdf_processor():
    # Create a simple PDF for testing
    pdf_path = TEST_DIR / "test.pdf"
    create_test_pdf(pdf_path)
    
    processor = PDFProcessor()
    chunks = processor.process(str(pdf_path))
    assert chunks is not None
    assert len(chunks) > 0
    assert all(hasattr(chunk, 'content') for chunk in chunks)

def test_audio_processor():
    # Create test audio file
    audio_path = TEST_DIR / "test.wav"
    create_test_audio(audio_path)
    
    processor = AudioProcessor()
    chunks = processor.process(str(audio_path))
    assert chunks is not None
    assert len(chunks) > 0
    assert all(hasattr(chunk, 'content') for chunk in chunks)

def test_video_processor():
    # Create test video file
    video_path = TEST_DIR / "test.mp4"
    create_test_video(video_path)
    
    processor = VideoProcessor()
    chunks = processor.process(str(video_path))
    assert chunks is not None
    assert len(chunks) > 0
    assert all(hasattr(chunk, 'content') for chunk in chunks)

def test_vector_store():
    store = ChromaStore()
    test_chunks = [
        {"content": "Test content 1", "metadata": {"source": "test1"}},
        {"content": "Test content 2", "metadata": {"source": "test2"}}
    ]
    
    # Test adding documents
    store.add_texts([chunk["content"] for chunk in test_chunks],
                   [chunk["metadata"] for chunk in test_chunks])
    
    # Test similarity search
    results = store.similarity_search("test content", k=1)
    assert len(results) == 1