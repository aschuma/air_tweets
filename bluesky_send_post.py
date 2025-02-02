from io import BytesIO
import json
from atproto import Client
from urllib.parse import urlparse
from typing import List, Dict, Any
import re

def send_bluesky_post(conf, message: str, image_bytes: bytes, timestamp: str):
    client = Client()
    client.login(conf['bluesky_handle'], conf['bluesky_password'])
    facets = calculate_bluesky_facets(message)
    # print(json.dumps(facets, indent=2))
    if image_bytes:
        client.send_image(text=message, image=BytesIO(
            image_bytes), image_alt='PM10 graph ' + timestamp, facets=facets)
    else:
        client.send_post(text=message, facets=facets)


class BlueSkyFacetCalculator:
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        self.text = text
        self.byte_text = text.encode('utf-8')

    def get_byte_position(self, char_position: int) -> int:
        """Convert character position to byte position."""
        return len(self.text[:char_position].encode('utf-8'))

    def is_valid_url(self, url: str) -> bool:
        """Validate URL structure."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def find_hashtags(self) -> List[Dict[str, Any]]:
        """Find hashtags and their byte positions."""
        return self._find_patterns(r'#[^\s#]+(?=\s|$)', "app.bsky.richtext.facet#tag", lambda match: match[1:])

    def find_urls(self) -> List[Dict[str, Any]]:
        """Find URLs and their byte positions."""
        return self._find_patterns(r'https?://[^\s]+(?=[.,;:!?)]*(?:\s|$))', "app.bsky.richtext.facet#link", self._clean_url)

    def _find_patterns(self, pattern: str, facet_type: str, process_match) -> List[Dict[str, Any]]:
        """Generic method to find patterns and their byte positions."""
        facets = []
        for match in re.finditer(pattern, self.text):
            content = process_match(match.group())
            if facet_type == "app.bsky.richtext.facet#link" and not self.is_valid_url(content):
                continue
            start = self.get_byte_position(match.start())
            end = self.get_byte_position(match.start() + len(content))
            facets.append({
                "index": {"byteStart": start, "byteEnd": end + 1},
                "features": [
                    {
                        "$type": facet_type,
                        "tag" if facet_type == "app.bsky.richtext.facet#tag" else "uri": content
                    }
                ]
            })
        return facets

    def _clean_url(self, url: str) -> str:
        """Remove trailing punctuation from URL."""
        return url.rstrip('.,;:!?)')

    def calculate_facets(self) -> List[Dict[str, Any]]:
        """Calculate all facets for the text."""
        try:
            hashtag_facets = self.find_hashtags()
            url_facets = self.find_urls()
            return sorted(
                hashtag_facets + url_facets,
                key=lambda x: x["index"]["byteStart"]
            )
        except Exception as e:
            raise RuntimeError(f"Error calculating facets: {str(e)}")


def calculate_bluesky_facets(text: str) -> List[Dict[str, Any]]:
    """Process a post and return its facets."""
    try:
        calculator = BlueSkyFacetCalculator(text)
        return calculator.calculate_facets()
    except Exception as e:
        print(f"Error processing post: {str(e)}")
        return []
