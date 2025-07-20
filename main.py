#!/usr/bin/env python3
"""
PDF Outline Extractor - Main Entry Point
Processes all PDFs in input directory and generates JSON outlines in output directory
"""

import os
import sys
import logging
import json
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    return logging.getLogger(__name__)

def main():
    """Main function to process all PDFs in input directory"""
    logger = setup_logging()
    
    logger.info("=== PDF OUTLINE EXTRACTOR STARTED ===")
    
    # Determine input and output directories
    if os.path.exists("/app/input"):
        # Docker environment
        input_dir = Path("/app/input")
        output_dir = Path("/app/output")
        logger.info("Running in Docker environment")
    else:
        # Local environment
        input_dir = Path("./input")
        output_dir = Path("./output")
        logger.info("Running in local environment")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir.absolute()} does not exist")
        logger.info("Please create an 'input' directory and place your PDF files there.")
        return False
    
    logger.info(f"Input directory: {input_dir.absolute()}")
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    logger.info(f"Searching for PDF files in: {input_dir.absolute()}")
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        # List all files in input directory for debugging
        all_files = list(input_dir.glob("*"))
        logger.info(f"Files found in input directory: {len(all_files)}")
        for file in all_files:
            logger.info(f"  - {file.name} ({file.suffix})")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files to process:")
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"  {i}. {pdf_file.name} ({pdf_file.stat().st_size} bytes)")
    
    # Import PDF processor
    try:
        from pdf_processor import PDFProcessor
        processor = PDFProcessor()
        logger.info("PDF processor loaded successfully")
    except ImportError as e:
        logger.error(f"Failed to import PDFProcessor: {e}")
        return False
    except Exception as e:
        logger.error(f"Error initializing PDFProcessor: {e}")
        return False
    
    # Process each PDF file
    successful_processed = 0
    total_files = len(pdf_files)
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"Processing {i}/{total_files}: {pdf_file.name}")
        
        try:
            # Extract outline
            result = processor.extract_outline(str(pdf_file))
            
            # Generate output filename
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            # Save JSON output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            # Log success with details
            title = result.get('title', 'No title')
            outline_count = len(result.get('outline', []))
            
            logger.info(f"✓ SUCCESS: {pdf_file.name} -> {output_filename}")
            logger.info(f"  Title: '{title}'")
            logger.info(f"  Headings found: {outline_count}")
            
            successful_processed += 1
            
        except Exception as e:
            logger.error(f"✗ ERROR processing {pdf_file.name}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            continue
    
    # Final summary
    logger.info("=== PROCESSING COMPLETE ===")
    logger.info(f"Successfully processed: {successful_processed}/{total_files} files")
    
    if successful_processed > 0:
        logger.info(f"Output files saved to: {output_dir.absolute()}")
        # List output files
        output_files = list(output_dir.glob("*.json"))
        logger.info(f"Generated {len(output_files)} JSON files:")
        for output_file in output_files:
            logger.info(f"  - {output_file.name}")
    
    return successful_processed > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
