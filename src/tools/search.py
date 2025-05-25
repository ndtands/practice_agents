from src.tools.tavily_search import TavilySearchResultsWithImages
from src.tools.decorators import create_logged_tool
from src.config.tools import SELECTED_SEARCH_ENGINE, SearchEngine
import logging
logger = logging.getLogger(__name__)


# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)

def get_web_search_tool(max_search_results: int):
    return LoggedTavilySearch(
        name="web_search",
        max_results=max_search_results,
        include_raw_content=True,
        include_images=True,
        include_image_descriptions=True,
    )

