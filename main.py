#!/usr/bin/env python3
"""
PDF Outline Extractor - Main Entry Point
Processes all PDFs in /app/input and generates JSON outlines in /app/output
"""

import os
import sys
import logging
import json
from pathlib import Path
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to process all PDFs in input directory"""
    # Check for directories in order of preference
    if os.path.exists("/app/input"):
        # Docker environment
        input_dir = Path("/app/input")
        output_dir = Path("/app/output")
    elif os.path.exists("./input"):
        # Local VS Code setup
        input_dir = Path("./input")
        output_dir = Path("./output")
    elif os.path.exists("./attached_assets"):
        # Development/testing with sample files
        input_dir = Path("./attached_assets")
        output_dir = Path("./output")
    else:
        # Create input directory if none exists
        input_dir = Path("./input")
        output_dir = Path("./output")
        input_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created input directory: {input_dir}")
        logger.info("Please place your PDF files in the 'input' directory and run again.")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists and has PDFs
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        logger.info("Please create an 'input' directory and place your PDF files there.")
        sys.exit(1)
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Process each PDF file
    successful_processed = 0
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Extract outline
            result = processor.extract_outline(str(pdf_file))
            
            # Generate output filename
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            # Save JSON output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Successfully processed: {pdf_file.name} -> {output_filename}")
            successful_processed += 1
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            continue
    
    logger.info(f"Processing complete. Successfully processed {successful_processed}/{len(pdf_files)} files")

if __name__ == "__main__":
    main()
