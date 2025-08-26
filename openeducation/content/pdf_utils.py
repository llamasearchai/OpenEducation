import logging
from typing import Any, Dict, List, Tuple

from pypdf import PdfReader
from pypdf.generic import Destination

from ..models.content_block import ContentBlock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_page_map(reader: PdfReader) -> Dict[int, int]:
    """Create a map from PDF object IDs to page numbers."""
    page_map = {}
    for i, page in enumerate(reader.pages):
        if page.indirect_reference:
            page_map[page.indirect_reference.idnum] = i
    return page_map

def _traverse_bookmarks(
    bookmarks: List[Any],
    reader: PdfReader,
    page_map: Dict[int, int],
    all_destinations: List[Tuple[int, int]],
    parent_title: str = ""
) -> List[ContentBlock]:
    """Recursively traverse bookmarks to extract hierarchical chapters."""
    blocks = []
    
    for i, bookmark in enumerate(bookmarks):
        if isinstance(bookmark, list):
            # This is a list of children for the previous bookmark. Recurse.
            # The previous bookmark was a Destination, so we use its title as the new parent.
            if blocks:
                new_parent_title = blocks[-1].title
                blocks.extend(_traverse_bookmarks(bookmark, reader, page_map, all_destinations, new_parent_title))
            continue

        title = bookmark.title
        # Create the full hierarchical title
        full_title = f"{parent_title}::{title}" if parent_title else title
        
        start_page_num = page_map.get(bookmark.page.idnum)
        if start_page_num is None:
            logger.warning(f"Could not find page number for bookmark '{title}'. Skipping.")
            continue

        # Find the end page by looking at the start page of the next destination
        current_dest_index = -1
        for idx, (pageNum, top) in enumerate(all_destinations):
            if pageNum == start_page_num:
                current_dest_index = idx
                break

        end_page_num = reader.pages[-1].page_number
        if current_dest_index != -1 and current_dest_index + 1 < len(all_destinations):
            end_page_num = all_destinations[current_dest_index + 1][0]
        else:
            # It's the last bookmark, so it goes to the end of the document.
            end_page_num = len(reader.pages) -1

        # Ensure end page is not before start page
        if end_page_num < start_page_num:
            end_page_num = start_page_num

        logger.info(f"Processing chapter '{full_title}': pages {start_page_num}-{end_page_num}")
        
        text = ""
        for page_num in range(start_page_num, end_page_num + 1):
            if 0 <= page_num < len(reader.pages):
                text += reader.pages[page_num].extract_text()
        
        logger.info(f"  -> Extracted {len(text)} characters.")
        
        if text.strip():
            blocks.append(
                ContentBlock.from_text(
                    source_id="pediatric_cardiology",
                    title=full_title,
                    body=text,
                )
            )

    return blocks

def _get_all_destinations(bookmarks: List[Any], page_map: Dict[int, int]) -> List[Tuple[int, int]]:
    """Flatten all destinations and sort them to determine page ranges."""
    destinations = []
    for item in bookmarks:
        if isinstance(item, Destination):
            page_num = page_map.get(item.page.idnum)
            if page_num is not None:
                destinations.append((page_num, item.top))
        elif isinstance(item, list):
            destinations.extend(_get_all_destinations(item, page_map))
    
    # Sort by page number, then by vertical position on the page (top is higher value)
    destinations.sort(key=lambda x: (x[0], -x[1] if x[1] is not None else 0))
    return destinations


def extract_chapters_from_pdf(
    path: str, source_id: str
) -> List[ContentBlock]:
    """Extracts content from a PDF, chunked by hierarchical bookmarks."""
    logger.info(f"Extracting chapters from {path}...")
    try:
        reader = PdfReader(path)
        if not reader.outline:
            logger.warning("No bookmarks found in PDF. Cannot extract chapters.")
            return []

        page_map = _get_page_map(reader)
        # Get a sorted list of all destinations to infer page ranges
        all_destinations = _get_all_destinations(reader.outline, page_map)
        
        chapters = _traverse_bookmarks(reader.outline, reader, page_map, all_destinations)
        
        logger.info(f"Successfully extracted {len(chapters)} chapters.")
        return chapters

    except Exception as e:
        logger.error(f"Failed to extract chapters from PDF {path}: {e}")
        # Re-raise the exception to see the full traceback in the agent output
        raise e
