# Standard Operating Procedure (SOP)
## OCR Compression System - Token Estimation & DeepSeek-OCR Integration

**Version**: 2.0  
**Last Updated**: 2025-01-15  
**Status**: Active

---

## 1. Token Estimation Rules

### 1.1 Pre-Scan Calculation

**Encoding**: Use `tiktoken` with `cl100k_base` encoding (GPT-4 tokenizer)

**Process**:
1. Scan all discovered source files
2. Calculate token count using `tiktoken.encoding_for_model("gpt-4")`
3. Sum total tokens across all files
4. Store as `pre_compression_tokens`

**Implementation**:
```python
import tiktoken

def estimate_pre_compression_tokens(files: List[FileInfo]) -> int:
    """Estimate tokens before compression using cl100k_base encoding."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    total_tokens = 0
    
    for file_info in files:
        try:
            content = Path(file_info.path).read_text(encoding='utf-8')
            tokens = encoding.encode(content)
            total_tokens += len(tokens)
        except Exception as e:
            # Skip files that can't be read
            continue
    
    return total_tokens
```

### 1.2 Post-Compression Estimation

**Formula**: `post_tokens = ceil(pre_tokens / 10)`, rounded up to nearest 10k

**Examples**:
- 491k pre → 500k post (ceil(491k/10) = 49.1k → round to 50k → display as 500k)
- 125k pre → 130k post (ceil(125k/10) = 12.5k → round to 13k → display as 130k)
- 87k pre → 90k post (ceil(87k/10) = 8.7k → round to 9k → display as 90k)

**Implementation**:
```python
def estimate_post_compression_tokens(pre_tokens: int) -> int:
    """Estimate tokens after DeepSeek-OCR compression."""
    # Apply 10x compression ratio
    compressed = math.ceil(pre_tokens / 10)
    
    # Round up to nearest 10k
    rounded = math.ceil(compressed / 10000) * 10000
    
    return rounded
```

### 1.3 Warning Thresholds

**Rule 1: Minimal Savings Warning (<50k tokens)**
- **Condition**: `pre_tokens < 50,000`
- **Message**: "⚠️ Minimal savings—proceed for standardization?"
- **Action**: Show warning but allow user to proceed
- **UI**: Yellow warning badge with explanation

**Rule 2: Not Recommended (<10k tokens)**
- **Condition**: `pre_tokens < 10,000`
- **Message**: "❌ Not recommended—compression overhead exceeds benefits"
- **Action**: Disable compression, show explanation
- **UI**: Red alert with recommendation to skip

**Implementation**:
```python
def get_compression_recommendation(pre_tokens: int) -> Dict[str, Any]:
    """Get recommendation based on token count."""
    if pre_tokens < 10000:
        return {
            'recommended': False,
            'severity': 'error',
            'message': 'Not recommended—compression overhead exceeds benefits',
            'action': 'disable'
        }
    elif pre_tokens < 50000:
        return {
            'recommended': True,
            'severity': 'warning',
            'message': 'Minimal savings—proceed for standardization?',
            'action': 'warn'
        }
    else:
        return {
            'recommended': True,
            'severity': 'success',
            'message': 'Significant compression benefits expected',
            'action': 'proceed'
        }
```

---

## 2. DeepSeek-OCR Insights

### 2.1 Compression Metrics

**Constants** (Embedded in code):
- **Compression Ratio**: 10x (1k text tokens → 100 vision tokens)
- **Accuracy**: 97%
- **Throughput**: 200k pages/day (average device)
- **Processing Time**: ~0.005s per page (average device)

**Configuration** (JSON):
```json
{
  "deepseek_ocr": {
    "compression_ratio": 10,
    "accuracy": 0.97,
    "throughput_pages_per_day": 200000,
    "avg_processing_time_per_page_seconds": 0.005,
    "text_to_vision_token_ratio": 0.1
  }
}
```

### 2.2 Display Rules

**Primary Display** (Always Visible):
- Compression Ratio: "10x"
- Accuracy: "97%"
- Estimated Processing Time: Calculated from page count

**Hidden Details** (Behind "Details" button):
- Vision token conversion (1k text → 100 vision tokens)
- Throughput capacity (200k pages/day)
- Technical implementation details
- Model architecture information

**Implementation**:
```python
# Backend calculation
def calculate_deepseek_insights(file_count: int, pre_tokens: int) -> Dict[str, Any]:
    """Calculate DeepSeek-OCR insights."""
    config = load_deepseek_config()
    
    # Estimate pages (rough: 1 file ≈ 1-3 pages)
    estimated_pages = file_count * 2
    
    # Calculate processing time
    processing_time_seconds = estimated_pages * config['avg_processing_time_per_page_seconds']
    processing_time_formatted = format_duration(processing_time_seconds)
    
    # Calculate throughput capacity
    pages_per_day = config['throughput_pages_per_day']
    capacity_percentage = (estimated_pages / pages_per_day) * 100
    
    return {
        'compression_ratio': config['compression_ratio'],
        'accuracy': config['accuracy'],
        'estimated_pages': estimated_pages,
        'processing_time': processing_time_formatted,
        'throughput_capacity': f"{capacity_percentage:.2f}%",
        'text_to_vision_ratio': config['text_to_vision_token_ratio'],
        'vision_tokens_estimate': int(pre_tokens * config['text_to_vision_token_ratio'])
    }
```

---

## 3. UI Component Usage (Operational Context)

**Note**: For complete design specifications, colors, spacing, typography, and styling, see `PROJECT_DESIGN_RULEBOOK.md` (SSOT). This section provides operational context only (how components function, not how they look).

### 3.1 Token Estimation Display

**Component Function**: Animated Token Bar
- **Purpose**: Display token counts before and after compression
- **Behavior**: Shows pre-compression token count, then animates to show post-compression estimate
- **Data Displayed**: 
  - Before compression: Total tokens from source files
  - After compression: Estimated tokens after DeepSeek-OCR processing
  - Savings: Percentage reduction calculated and displayed
- **Recommendation Logic**: System evaluates token thresholds and displays appropriate recommendation badge
- **Design Specifications**: See `PROJECT_DESIGN_RULEBOOK.md` Section 4 (Color Palette) and Section 5 (Components) for color coding, animations, and styling

### 3.2 Insights Panel

**Component Function**: Collapsible Section
- **Purpose**: Display DeepSeek-OCR insights and technical details
- **Default State**: Collapsed, showing summary metrics only
- **Expanded State**: Full technical details visible
- **Toggle Mechanism**: User clicks header or toggle button to expand/collapse
- **Summary Metrics Displayed**: Compression ratio, accuracy percentage, estimated processing time
- **Detailed Metrics Displayed**: Estimated pages, text tokens, vision tokens, conversion ratio, throughput capacity, model version
- **Design Specifications**: See `PROJECT_DESIGN_RULEBOOK.md` Section 5 (Components & Interactivity) for animation, layout, and styling details

### 3.3 History Table

**Component Function**: Job History Display
- **Purpose**: Show list of compression jobs with status and metrics
- **Data Columns**: Job ID, Status, Started At, Progress, Actions
- **Features**: 
  - Auto-refresh every 5 seconds
  - Status badges for job state (completed, failed, running, queued)
  - Progress indicators for active jobs
  - Action buttons for completed jobs (Open Folder)
- **Token Estimates**: Displayed when available (pre-compression, post-compression, compression ratio)
- **Design Specifications**: See `PROJECT_DESIGN_RULEBOOK.md` Section 5 (Components) for table styling, badges, and button patterns

---

## 4. Backend Infrastructure

### 4.1 Token Estimation Service

**Class**: `TokenEstimationService`

**Responsibilities**:
- Pre-scan token calculation
- Post-compression estimation
- Warning threshold evaluation
- Integration with file discovery

**Methods**:
```python
class TokenEstimationService:
    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.config = self._load_config()
    
    def estimate_pre_compression(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Estimate tokens before compression."""
        total_tokens = 0
        file_tokens = {}
        
        for file_info in files:
            tokens = self._count_file_tokens(file_info)
            file_tokens[file_info.path] = tokens
            total_tokens += tokens
        
        return {
            'total_tokens': total_tokens,
            'file_tokens': file_tokens,
            'file_count': len(files)
        }
    
    def estimate_post_compression(self, pre_tokens: int) -> Dict[str, Any]:
        """Estimate tokens after compression."""
        compressed = math.ceil(pre_tokens / 10)
        rounded = math.ceil(compressed / 10000) * 10000
        
        savings = pre_tokens - rounded
        savings_percent = (savings / pre_tokens) * 100
        
        return {
            'estimated_tokens': rounded,
            'savings': savings,
            'savings_percent': savings_percent,
            'compression_ratio': pre_tokens / rounded if rounded > 0 else 0
        }
    
    def get_recommendation(self, pre_tokens: int) -> Dict[str, Any]:
        """Get compression recommendation."""
        return get_compression_recommendation(pre_tokens)
```

### 4.2 DeepSeek Insights Service

**Class**: `DeepSeekInsightsService`

**Responsibilities**:
- Calculate processing metrics
- Format insights for display
- Load configuration from JSON

**Methods**:
```python
class DeepSeekInsightsService:
    def __init__(self, config_path: Path = None):
        self.config = self._load_config(config_path)
    
    def calculate_insights(self, file_count: int, pre_tokens: int) -> Dict[str, Any]:
        """Calculate DeepSeek-OCR insights."""
        estimated_pages = file_count * 2  # Rough estimate
        processing_time = estimated_pages * self.config['avg_processing_time_per_page_seconds']
        
        return {
            'compression_ratio': self.config['compression_ratio'],
            'accuracy': self.config['accuracy'],
            'estimated_pages': estimated_pages,
            'processing_time_seconds': processing_time,
            'processing_time_formatted': self._format_duration(processing_time),
            'throughput_capacity_percent': (estimated_pages / self.config['throughput_pages_per_day']) * 100,
            'text_to_vision_ratio': self.config['text_to_vision_token_ratio'],
            'vision_tokens_estimate': int(pre_tokens * self.config['text_to_vision_token_ratio'])
        }
    
    def _load_config(self, config_path: Path = None) -> Dict[str, Any]:
        """Load DeepSeek configuration."""
        if config_path is None:
            config_path = Path(__file__).parent / 'configs' / 'deepseek_ocr.json'
        
        if config_path.exists():
            return json.loads(config_path.read_text())
        else:
            # Default configuration
            return {
                'compression_ratio': 10,
                'accuracy': 0.97,
                'throughput_pages_per_day': 200000,
                'avg_processing_time_per_page_seconds': 0.005,
                'text_to_vision_token_ratio': 0.1
            }
```

---

## 5. Testing Requirements

### 5.1 Token Estimation Tests

**Test Cases**:
1. Pre-scan calculation accuracy
2. Post-compression rounding (491k → 500k)
3. Warning threshold at 50k
4. Error threshold at 10k
5. Edge cases (empty files, binary files, encoding errors)

**Test Implementation**:
```python
def test_token_estimation_warning_threshold():
    """Test warning threshold at 50k tokens."""
    service = TokenEstimationService()
    
    # Test at threshold boundary
    result = service.get_recommendation(50000)
    assert result['severity'] == 'success'
    
    result = service.get_recommendation(49999)
    assert result['severity'] == 'warning'
    assert 'Minimal savings' in result['message']
    
    result = service.get_recommendation(10000)
    assert result['severity'] == 'error'
    assert 'Not recommended' in result['message']
```

### 5.2 DeepSeek Insights Tests

**Test Cases**:
1. Processing time calculation
2. Throughput capacity percentage
3. Vision token conversion
4. Configuration loading

---

## 6. Integration Points

### 6.1 File Discovery Integration

- Run token estimation after file discovery completes
- Store estimates in pipeline state
- Pass estimates to UI via API

### 6.2 Pipeline Integration

- Display estimates before compression starts
- Show warnings if thresholds met
- Update estimates during compression (if applicable)

### 6.3 UI Integration

- Token bar component (animated)
- Collapsible insights panel
- History table with estimates
- Warning/error displays

---

## 7. Previous Rules (Retained)

### 7.1 File Selection Rules
- Exclude: node_modules, dist, android, latest, .git, build artifacts
- Include: .ts, .tsx, .js, .jsx, .json, .yaml, .yml, .css, .html
- Handle encoding errors gracefully

### 7.2 Append Rules
- Preserve directory structure in output
- Maintain file naming conventions
- Add metadata headers to PDFs

### 7.3 Optimization Rules
- Parallel processing (configurable workers)
- Resume capability (checkpoint-based)
- Retry logic (exponential backoff)
- Progress tracking (real-time updates)

---

## 8. Constants Reference

```python
# Token Estimation Constants
TOKEN_ENCODING = "cl100k_base"  # GPT-4 tokenizer
COMPRESSION_RATIO = 10  # 10x compression
ROUNDING_INCREMENT = 10000  # Round to nearest 10k
WARNING_THRESHOLD = 50000  # Warn below 50k tokens
ERROR_THRESHOLD = 10000  # Error below 10k tokens

# DeepSeek-OCR Constants
DEEPSEEK_COMPRESSION_RATIO = 10
DEEPSEEK_ACCURACY = 0.97
DEEPSEEK_THROUGHPUT_PAGES_PER_DAY = 200000
DEEPSEEK_AVG_TIME_PER_PAGE = 0.005  # seconds
TEXT_TO_VISION_TOKEN_RATIO = 0.1  # 1k text → 100 vision
```

---

**End of SOP**

