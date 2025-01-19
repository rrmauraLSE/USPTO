# Patent Gender Bias Analysis

## Overview
This project investigates potential gender bias in patent application reviews
using causal inference methods and deep learning. It is part of my PhD thesis
developing statistical theory for causal regression with high-dimensional 
data (images and text) using double debiased machine learning.

## Research Question
Does an applicant's gender causally affect their probability of patent 
acceptance? The project aims to detect if patent reviewers exhibit systematic
bias based on applicant gender.

### Methodological Approach
While a randomized control trial would be ideal (randomly assigning authors to
patents), this is infeasible. Instead, the project combines:
- Causal inference techniques
- Econometric methods  
- Deep learning models
- Double debiased machine learning to avoid estimation bias

## Project Structure

### Data Collection
`download_patent_data.py`
- Downloads patent application data from USPTO
- Handles both text-only and image-embedded TIFF files
- Configurable by year range
- Supports both application and grant data types

### Data Processing 
`process_patent_xml.py`
- Extracts structured data from USPTO XML files
- Processes metadata: titles, publication details, classifications
- Handles inventor information
- Parses abstracts, descriptions, and claims
- Manages compressed file extraction
- Calculates text statistics
- Outputs to parquet format

### Model Infrastructure
`gpt4_parallel_processing.py`
- Implements asynchronous OpenAI API client
- Enables parallel processing of GPT-4 requests
- Handles rate limiting and error management
- Supports both chat completions and embeddings

### Text Embedding Generation
`generate_embeddings.py`
- Converts patent text data to embeddings using OpenAI models
- Handles text segmentation for long documents
- Implements efficient batch processing
- Manages API rate limits
- Supports multiple embedding models:
  - text-embedding-ada-002 (1536d)
  - text-embedding-3-small (1536d)
  - text-embedding-3-large (3072d)

## Technical Details
- Asynchronous processing for API efficiency
- Robust error handling and rate limiting
- Modular design for maintainability
- Comprehensive data preprocessing pipeline
- Scalable architecture for large dataset processing

## Dependencies
- OpenAI API
- pandas
- asyncio
- aiohttp
- BeautifulSoup
- tiktoken
- tqdm

## Usage
1. Configure API keys and parameters
2. Run data collection script
3. Process XML files into structured format
4. Generate embeddings for analysis
5. Apply causal inference methods (TODO)
