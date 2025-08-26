# Agents Integration

OpenEducation integrates the **OpenAI Agents SDK** for multi-agent orchestration. The orchestration agent (`openeducation/agents/flow.py`) uses function tools to invoke pipeline steps:

## Architecture

### Core Components

- **Safety Agent**: Content safety and appropriateness checking
- **Conductor Agent**: Orchestrates the complete pipeline
- **Function Tools**: Individual pipeline steps as callable functions

### Agent Flow

```
Content Input → Safety Check → Pipeline Steps → Quality Validation → Output
```

## Function Tools

### ingest_sources(cfg: Dict)

Ingests content from configured sources and extracts terms.

**Parameters:**
- `cfg`: Configuration dictionary with sources

**Returns:**
- Path to content blocks JSON file

### build_rag_index(blocks_path: str)

Builds RAG index from content blocks using embeddings.

**Parameters:**
- `blocks_path`: Path to content blocks JSON

**Returns:**
- Path to index JSON file

### generate_cards(blocks_path: str, deck_id: str, max_cards: int)

Generates flashcards from content blocks.

**Parameters:**
- `blocks_path`: Path to content blocks JSON
- `deck_id`: Identifier for the deck
- `max_cards`: Maximum number of cards to generate

**Returns:**
- Path to cards JSON file

### assemble_deck(cards_path: str, deck_id: str, name: str)

Assembles Anki deck from generated cards.

**Parameters:**
- `cards_path`: Path to cards JSON
- `deck_id`: Identifier for the deck
- `name`: Human-readable deck name

**Returns:**
- Path to Anki package (.apkg) file

### push_to_anki(apkg_path: str)

Pushes deck to Anki via AnkiConnect.

**Parameters:**
- `apkg_path`: Path to Anki package file

**Returns:**
- Success message with import statistics

## Safety Mechanisms

### Content Safety

The safety agent checks content for:
- Harmful or inappropriate material
- Medical content restrictions
- Language compliance
- Content quality thresholds

### Pipeline Safety

- Graceful error handling at each step
- Validation checkpoints between stages
- Fallback mechanisms for failed steps
- Comprehensive logging and monitoring

## Configuration

### Agent Settings

```json
{
  "safety": {
    "allow_medical_actions": false,
    "language": "en",
    "content_filters": ["harmful", "inappropriate"]
  },
  "agents": {
    "conductor_model": "gpt-4.1",
    "safety_model": "gpt-4.1",
    "temperature": 0.2
  }
}
```

## Usage Examples

### Basic Pipeline

```python
from openeducation.agents.flow import run_pipeline

config_json = """
{
  "data_dir": "data",
  "sources": [{"id": "src1", "type": "markdown", "path": "content.md"}],
  "deck": {"id": "deck1", "name": "My Deck"}
}
"""

result = await run_pipeline(config_json)
print(result)
```

### Custom Agent Flow

```python
from openeducation.agents.tools import ingest_sources, generate_cards

# Custom orchestration
blocks_path = ingest_sources(config)
cards_path = generate_cards(blocks_path, "custom_deck", 50)
# Add custom validation or processing
```

## Error Handling

### Common Error Patterns

- **Source ingestion failures**: File not found, unsupported format
- **Embedding failures**: Memory issues, API limits
- **Card generation failures**: Content quality, LLM API errors
- **Anki integration failures**: Connection issues, deck conflicts

### Recovery Strategies

1. **Retry mechanisms** for transient failures
2. **Fallback methods** for alternative processing
3. **Partial success handling** for large batches
4. **Detailed error reporting** for debugging

## Performance Considerations

### Optimization Strategies

- **Batch processing** for large content sets
- **Caching** of embeddings and intermediate results
- **Parallel processing** for independent operations
- **Resource monitoring** and adaptive scaling

### Monitoring

- **Pipeline metrics**: Success rates, processing times
- **Resource usage**: Memory, API calls, disk space
- **Quality metrics**: Card quality scores, duplication rates
- **Error tracking**: Failure patterns and resolution times

## Extension Points

### Custom Tools

Add new function tools by creating functions in `agents/tools.py`:

```python
def custom_processing(input_path: str) -> str:
    """Custom processing function."""
    # Implementation
    return output_path
```

### Custom Agents

Extend the conductor agent in `agents/flow.py`:

```python
def custom_conductor_agent(cfg_json: str) -> str:
    """Custom orchestration logic."""
    # Implementation
    return result
```

## Best Practices

### Agent Design

1. **Single responsibility**: Each tool has one clear purpose
2. **Error resilience**: Handle failures gracefully
3. **Logging**: Comprehensive logging for debugging
4. **Validation**: Input/output validation at each step

### Pipeline Design

1. **Modularity**: Independent, composable steps
2. **Observability**: Metrics and monitoring
3. **Scalability**: Handle varying content sizes
4. **Maintainability**: Clear interfaces and documentation
