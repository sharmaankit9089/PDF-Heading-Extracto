# Enhanced PDF Outline Extractor

A robust, Docker-containerized Python application that extracts hierarchical document outlines from PDF files, generating structured JSON output with titles, headings (H1, H2, H3, H4), and page numbers. Built specifically for the hackathon challenge "Connecting the Dots Through Docs".

## 🚀 Features

- **Multi-Strategy Heading Detection**: Uses pattern matching, font analysis, structural analysis, and contextual cues
- **Robust Title Extraction**: Advanced title detection from PDF metadata, text analysis, and TOC
- **High Accuracy**: Comprehensive pattern recognition for various document types
- **Fast Processing**: Extracts outlines from up to 50-page PDFs within 10 seconds
- **Hierarchical Structure**: Accurately identifies H1, H2, H3, H4 heading levels
- **Error Resilience**: Graceful handling of malformed PDFs and edge cases
- **Offline Operation**: Works without internet connectivity as required
- **Docker Compatible**: Runs on AMD64 architecture with CPU-only execution
- **Batch Processing**: Processes all PDFs in input directory automatically

## 📋 Requirements

- Docker installed on your system
- PDFs to process (up to 50 pages each)
- AMD64 (x86_64) architecture compatibility

## 🔧 Quick Start

### Option 1: Docker Deployment (Production/Submission)

#### 1. Build the Docker Image
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
```

#### 2. Prepare Input Directory
```bash
mkdir input output
# Place your PDF files in the input directory
```

#### 3. Run the Container
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:latest
```

### Option 2: Direct Python Execution (Development)

#### Prerequisites
- Python 3.9+
- PyMuPDF library

#### 1. Install Dependencies
```bash
pip install PyMuPDF>=1.24.0
```

#### 2. Run the Application
```bash
python main.py
```

The application automatically detects and processes PDFs from:
1. `./input` directory (preferred for local development)
2. `./attached_assets` directory (for testing with sample files)
3. Creates `./input` directory if none exists

## 📁 Project Structure

```
pdf-outline-extractor/
├── main.py                 # Main application entry point
├── pdf_processor.py        # Core PDF processing and title extraction
├── heading_detector.py     # Advanced heading detection algorithms
├── Dockerfile             # Container configuration
├── README.md              # This documentation
├── input/                 # Input PDF files (create this directory)
├── output/                # Generated JSON files
└── attached_assets/       # Sample files and documentation
```

## 📊 Output Format

The application generates JSON files with the following structure:

```json
{
    "title": "Understanding AI: A Comprehensive Guide",
    "outline": [
        {
            "level": "H1",
            "text": "Introduction",
            "page": 1
        },
        {
            "level": "H2",
            "text": "What is Artificial Intelligence?",
            "page": 2
        },
        {
            "level": "H3",
            "text": "Machine Learning Fundamentals",
            "page": 3
        },
        {
            "level": "H2",
            "text": "Applications and Use Cases",
            "page": 5
        }
    ]
}
```

## 🔍 Detection Algorithms

### Title Extraction
1. **PDF Metadata Analysis**: Extracts title from document properties
2. **Font-Based Scoring**: Analyzes font size, weight, and positioning
3. **Pattern Recognition**: Identifies common title patterns (RFP, Understanding, etc.)
4. **TOC Integration**: Uses table of contents when available

### Heading Detection Strategies

#### 1. Pattern-Based Detection (Highest Confidence)
- **H1 Patterns**: CHAPTER, SECTION, Introduction, Overview, Executive Summary
- **H2 Patterns**: Numbered sections (1., A.), Background, Methodology, Results
- **H3 Patterns**: Multi-level numbering (1.1.1), lettered items (a), phases
- **H4 Patterns**: Deep numbering (1.1.1.1), specific subsections

#### 2. Font-Based Classification
- Analyzes font size relative to document averages
- Considers bold/italic formatting
- Weighs text length and positioning

#### 3. Structural Analysis
- Recognizes numbered and lettered section formats
- Identifies Roman numeral patterns
- Detects hierarchical numbering schemes

#### 4. Contextual Classification
- Common heading vocabulary recognition
- Text length and capitalization analysis
- Sentence structure evaluation

## ⚡ Performance Specifications

| Metric | Requirement | Status |
|--------|-------------|---------|
| Processing Speed | ≤ 10 seconds for 50-page PDF | ✅ Optimized |
| Model Size | ≤ 200MB | ✅ CPU-only, no models |
| Network Access | Offline operation | ✅ No internet calls |
| Architecture | AMD64 (x86_64) | ✅ Docker compatible |
| Memory Usage | Standard container limits | ✅ Efficient processing |

## 🧪 Testing Your Setup

1. **Prepare Test Files**:
   ```bash
   mkdir input
   # Copy sample PDFs to input directory
   ```

2. **Run Processing**:
   ```bash
   python main.py
   ```

3. **Verify Output**:
   ```bash
   ls output/
   # Check generated JSON files
   ```

4. **Validate JSON Structure**:
   ```bash
   python -m json.tool output/sample.json
   ```

## 🔧 Configuration

### Environment Variables
- `PYTHONPATH=/app` (automatically set in Docker)
- `PYTHONUNBUFFERED=1` (for proper logging in containers)

### Logging
The application provides comprehensive logging:
- Processing status for each PDF
- Error details for failed extractions
- Performance metrics and warnings

## 🛠️ Advanced Usage

### Custom Pattern Addition
To add domain-specific heading patterns, modify `heading_detector.py`:

```python
# Add to appropriate pattern list
self.h2_patterns.append(r'^Your\s+Custom\s+Pattern')
```

### Font Threshold Adjustment
Modify font analysis thresholds in `HeadingDetector.__init__()`:

```python
self.font_thresholds = {
    "large_heading": 18,    # Adjust as needed
    "medium_heading": 16,
    "small_heading": 14
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"No PDFs found"**
   - Ensure PDFs are in the correct input directory
   - Check file extensions are `.pdf`

2. **"Permission denied"**
   - Verify read permissions on input directory
   - Check write permissions on output directory

3. **"Empty output"**
   - Confirm PDFs contain text (not scanned images)
   - Check logs for processing errors

4. **Docker build issues**
   - Ensure Docker supports `linux/amd64` platform
   - Verify sufficient disk space

### Debug Mode
Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Algorithm Accuracy

The system uses multiple validation layers:

1. **Pattern Validation**: High-confidence regex matching
2. **Font Analysis**: Document-specific threshold adaptation
3. **Hierarchy Consistency**: Logical heading level validation
4. **Duplicate Removal**: Text-based deduplication
5. **Quality Filtering**: Removes page artifacts and noise

## 🔒 Security & Compliance

- **Offline Operation**: No network access prevents data leakage
- **Memory Management**: Efficient PDF processing with proper cleanup
- **Error Handling**: Graceful failure without exposing system details
- **Input Validation**: Robust handling of malformed PDFs

## 📝 Development Notes

### Code Architecture
- **Modular Design**: Separate concerns for processing and detection
- **Error Resilience**: Comprehensive exception handling
- **Performance Optimization**: Efficient text processing and memory usage
- **Extensible Patterns**: Easy addition of new heading detection rules

### Best Practices Implemented
- Type hints for better code maintenance
- Comprehensive logging for debugging
- Clean separation of PDF processing and heading detection
- Robust text cleaning and normalization
- Hierarchical validation for output quality

## 📄 License & Attribution

Built for the hackathon challenge "Round 1A: Understand Your Document - Connecting the Dots Through Docs". This solution demonstrates advanced PDF processing techniques for document structure extraction.

---

For technical support or questions about the implementation, refer to the detailed code comments and logging output during processing.