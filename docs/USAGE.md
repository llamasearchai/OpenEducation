# Usage Guide

## CLI Commands

### Initialize Configuration

```bash
python -m openeducation.cli init [path]
```

Creates a sample configuration file with default settings.

### Ingest Content

```bash
python -m openeducation.cli ingest config.json [out_dir]
```

Ingests content from configured sources and extracts terms.

### Build RAG Index

```bash
python -m openeducation.cli index content_blocks.json
```

Builds vector embeddings for content retrieval.

### Generate Cards

```bash
python -m openeducation.cli generate content_blocks.json [deck_id] [max_cards]
```

Generates flashcards using rule-based or LLM methods.

### Export Anki Deck

```bash
python -m openeducation.cli export cards.json [deck_id] [name]
```

Exports cards to Anki package format (.apkg).

### Push to Anki

```bash
python -m openeducation.cli push deck.apkg
```

Imports deck into Anki via AnkiConnect.

### Run Agents Pipeline

```bash
python -m openeducation.cli run_agents config.json [--push-to-anki]
```

Orchestrates the complete pipeline using multi-agent system.

### Validate Content

```bash
python -m openeducation.cli validate [run_dir]
```

Runs quality assurance checks on generated cards.

### Preview Cards

```bash
python -m openeducation.cli preview [run_dir] [n]
```

Displays first N cards for review.

### Generate Reports

```bash
python -m openeducation.cli report config.json [run_dir]
```

Creates manifest and licensing reports.

### Start Preview Server

```bash
python -m openeducation.cli serve [host] [port]
```

Starts FastAPI server for deck preview.

## Configuration

### Source Configuration

```json
{
  "id": "source_id",
  "type": "markdown|text|pdf|json|csv",
  "path": "/path/to/content",
  "tags": ["tag1", "tag2"],
  "license": "CC-BY"
}
```

### Deck Configuration

```json
{
  "id": "deck_id",
  "name": "Deck Name",
  "description": "Deck description",
  "tags": ["tag1"]
}
```

### LLM Configuration

```json
{
  "provider": "openai|none",
  "model": "gpt-4.1",
  "temperature": 0.2
}
```

### RAG Configuration

```json
{
  "embedder": "hash|openai",
  "embedding_model": "text-embedding-3-small",
  "dims": 512,
  "top_k": 5
}
```

## File Formats

### Supported Input Formats

- **Markdown**: `.md` files with headers and bullet points
- **PDF**: Text-extractable PDF documents
- **Text**: Plain text files
- **JSON**: Structured content
- **CSV**: Tabular data

### Output Formats

- **JSON**: Cards, manifests, reports
- **APKG**: Anki package files
- **HTML**: Preview interface

## Best Practices

### Content Preparation

1. Use clear headers and bullet points
2. Include key terms and definitions
3. Break complex topics into sections
4. Add licensing information

### Quality Assurance

1. Run validation after generation
2. Preview cards before export
3. Check for duplicates and low-quality content
4. Review readability scores

### Performance Optimization

1. Use appropriate chunk sizes
2. Configure embedding dimensions
3. Limit cards per content block
4. Use hash embeddings for speed

## Troubleshooting

### Common Issues

- **Missing dependencies**: Run `pip install -r requirements.txt`
- **PDF extraction fails**: Ensure PDFs contain selectable text
- **Anki connection fails**: Check AnkiConnect plugin is installed
- **Large files**: Split into smaller chunks or increase memory

### Debug Mode

Set environment variable for detailed logging:

```bash
export OPENEDUCATION_DEBUG=1
python -m openeducation.cli command
```
