"""
Integration test for the full PPT generation pipeline
Tests the new JSON-based agents and the HTML/PDF rendering.
"""
import sys
import os
import logging
import json

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

from project_manager import PPTProjectManager

def test_full_pipeline():
    print("=" * 60)
    print("TESTING FULL AGENTIC PIPELINE (JSON OUTPUT) -> PDF")
    print("=" * 60)

    # Initialize the project manager
    # Passing no socketio so it just runs locally
    pm = PPTProjectManager() 

    # We will test a small topic with 3 slides
    topic = "The Voyager 1 Space Probe"
    num_slides = 3
    
    print(f"Topic: {topic}")
    print(f"Slides: {num_slides}")
    
    try:
        # This will trigger the crew -> JSON output -> _create_html_presentation -> PDF
        result = pm.generate_presentation(topic, num_slides=num_slides)
        
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY ✅")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            pdf_path = result.get('pdf_path')
            if pdf_path and os.path.exists(pdf_path):
                print(f"✅ Verified PDF generated at: {pdf_path}")
            else:
                print("❌ PDF path missing or file does not exist")
        else:
            print("❌ Pipeline reported failure")
            
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ PIPELINE FAILED: {e}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    test_full_pipeline()
