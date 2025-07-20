# PDF Outline Extractor - Generic Solution

A robust, Docker-containerized Python application that extracts hierarchical document outlines from **any PDF files** (up to 50 pages), generating structured JSON output with titles, headings (H1, H2, H3, H4), and page numbers. Built for the hackathon challenge "Connecting the Dots Through Docs" with intelligent algorithms that work across different document types and formats.

## 🚀 Quick Start

### Method 1: Direct Python Execution (Recommended for Development)

#### Prerequisites
- Python 3.9+ installed
- PyMuPDF library

#### 1. Install Dependencies
```bash
pip install PyMuPDF>=1.24.0
```

#### 2. Prepare Your Files
```bash
# Place your PDF files in the input directory
mkdir -p input output
# Copy any PDF files (up to 50 pages each) to the input directory
```

#### 3. Run the Application
```bash
python main.py
```

### Method 2: Docker Deployment (Production/Submission)

#### 1. Build the Docker Image
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
```

#### 2. Prepare Input Directory
```bash
mkdir -p input output
# Place your PDF files in the input directory
```

#### 3. Run the Container
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:latest
```

## 📊 Output Format

The application generates JSON files with the following structure:

```json
{
    "title": "Annual Report 2023: Financial Analysis",
    "outline": [
        {
            "level": "H1",
            "text": "Executive Summary",
            "page": 1
        },
        {
            "level": "H2", 
            "text": "1.1 Key Findings",
            "page": 2
        },
        {
            "level": "H3",
            "text": "Financial Performance", 
            "page": 3
        },
        {
            "level": "H4",
            "text": "a) Revenue Growth",
            "page": 4
        }
    ]
}
```

## 🔧 Project Structure

```
pdf-outline-extractor/
├── main.py                 # Main application entry point
├── pdf_processor.py        # Core PDF processing and title extraction
├── heading_detector.py     # Advanced heading detection algorithms
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── README.md              # This documentation
├── input/                 # Input PDF files (create this directory)
└── output/                # Generated JSON files
```

## 📋 Key Features

- **Universal PDF Support**: Works with any PDF document type (reports, papers, manuals, etc.)
- **Multi-Strategy Title Extraction**: Uses metadata, font analysis, and content patterns
- **Intelligent Heading Detection**: Combines pattern matching, font analysis, and structural recognition
- **Hierarchical Structure**: Accurately identifies H1, H2, H3, H4 heading levels
- **Fast Processing**: Extracts outlines from up to 50-page PDFs within 10 seconds
- **Error Resilience**: Graceful handling of malformed PDFs and edge cases
- **Offline Operation**: Works without internet connectivity as required
- **Docker Compatible**: Runs on AMD64 architecture with CPU-only execution
- **Batch Processing**: Processes all PDFs in input directory automatically

## 🧠 Advanced Algorithms

### Multi-Strategy Heading Detection

1. **Pattern Matching**: Recognizes common heading patterns
   - Numbered sections: "1. Introduction", "1.1 Background"
   - All caps headings: "CHAPTER 1", "OVERVIEW"
   - Standard sections: "Introduction", "Methodology", "Conclusion"

2. **Font Analysis**: Analyzes document typography
   - Identifies larger fonts as higher-level headings
   - Considers bold/italic formatting
   - Adapts to each document's font patterns

3. **Structural Analysis**: Recognizes document organization
   - Hierarchical numbering (1.1.1.1)
   - Lettered sections (a), (b), (c)
   - Roman numerals (I, II, III)

4. **Content Classification**: Uses semantic understanding
   - Common heading vocabulary
   - Context-aware classification
   - Length and capitalization patterns

### Smart Title Extraction

1. **PDF Metadata**: Extracts from document properties (when available and meaningful)
2. **Font-Based Detection**: Identifies titles by size, position, and formatting
3. **Pattern Recognition**: Recognizes common title formats and structures
4. **Content Analysis**: Uses semantic patterns to identify document titles

## ⚡ Performance Specifications

| Metric | Requirement | Status |
|--------|-------------|---------|
| Processing Speed | ≤ 10 seconds for 50-page PDF | ✅ Optimized |
| Model Size | ≤ 200MB | ✅ CPU-only, no models |
| Network Access | Offline operation | ✅ No internet calls |
| Architecture | AMD64 (x86_64) | ✅ Docker compatible |
| Document Types | Any PDF format | ✅ Universal support |

## 🧪 Testing Your Setup

1. **Prepare Test Files**:
   ```bash
   mkdir input
   # Copy any PDF files to input directory
   # Examples: research papers, reports, manuals, books, etc.
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
   python -m json.tool output/your-document.json
   ```

## 🛠️ Supported Document Types

The solution works with various PDF document types:

- **Academic Papers**: Research papers, theses, dissertations
- **Business Documents**: Reports, proposals, white papers
- **Technical Manuals**: User guides, API documentation, specifications
- **Books**: Textbooks, reference materials, e-books
- **Government Documents**: Policies, regulations, forms
- **Financial Reports**: Annual reports, financial statements
- **Legal Documents**: Contracts, legal briefs, regulations

## 📝 Heading Recognition Examples

### H1 (Major Sections)
- `INTRODUCTION`
- `1. Overview`
- `CHAPTER 1`
- `Executive Summary`
- `Table of Contents`
- `References`

### H2 (Section Headings)
- `1.1 Background`
- `Methodology`
- `Phase I`
- `Summary:`
- `Key Findings`

### H3 (Subsections)
- `1.1.1 Objectives`
- `a) First item`
- `Timeline:`
- `Requirements:`
- `A. Initial Phase`

### H4 (Sub-subsections)
- `1.1.1.1 Details`
- `(a) Sub-item`
- `i. Specific point`
- `Step 1:`

## 🚨 Troubleshooting

### Common Issues

1. **"No PDFs found"**
   - Ensure PDFs are in the `input` directory
   - Check file extensions are `.pdf`

2. **"Permission denied"**
   - Verify read permissions on input directory
   - Check write permissions on output directory

3. **"Empty output"**
   - Confirm PDFs contain text (not scanned images)
   - Check logs for processing errors
   - Some PDFs may have no detectable headings

4. **Docker build issues**
   - Ensure Docker supports `linux/amd64` platform
   - Verify sufficient disk space

### Optimizing Results

- **For better heading detection**: Ensure PDFs have proper text formatting
- **For better titles**: Documents with metadata or clear title formatting work best
- **For complex documents**: The algorithm adapts to different document structures automatically

### Debug Mode
Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Dependencies

- **PyMuPDF>=1.24.0**: PDF processing and text extraction
- **Python 3.9+**: Runtime environment

## 🔒 Security & Compliance

- **Offline Operation**: No network access prevents data leakage
- **Memory Management**: Efficient PDF processing with proper cleanup
- **Error Handling**: Graceful failure without exposing system details
- **Input Validation**: Robust handling of malformed PDFs

---

## 💻 VS Code Execution Instructions

To run this solution in VS Code:

1. **Open Terminal in VS Code** (Ctrl+` or View → Terminal)

2. **Navigate to project directory**:
   ```bash
   cd /path/to/your/project  # Replace with your actual path
   ```

3. **Install dependencies**:
   ```bash
   pip install PyMuPDF>=1.24.0
   ```

4. **Create input directory and add PDFs**:
   ```bash
   mkdir -p input output
   # Copy any PDF files to the input directory
   # The solution works with any PDF type (reports, papers, manuals, etc.)
   ```

5. **Run the solution**:
   ```bash
   python main.py
   ```

6. **Check the results**:
   ```bash
   ls output/
   # View generated JSON files
   cat output/your-document.json  # Example to view a specific output
   ```

The solution will automatically process all PDF files in the `input` directory and generate corresponding JSON files in the `output` directory. It uses intelligent algorithms to detect headings and extract titles from any type of PDF document within the 50-page limit.

## 🎯 Algorithm Highlights

- **Adaptive Font Analysis**: Automatically adjusts to each document's font patterns
- **Context-Aware Detection**: Uses semantic understanding for better classification  
- **Hierarchy Validation**: Ensures logical heading progression
- **Multi-Language Support**: Works with documents in different languages
- **Format Agnostic**: Handles various PDF creation tools and formats

This solution is designed to work robustly across different document types, layouts, and formatting styles while maintaining high accuracy and performance standards required for the hackathon challenge.