from io import BytesIO
from mastodon import Mastodon
from config import mastodon_access_token, mastodon_api_base_url, conf_luftdaten_graph_mime_type


def send_mastodon_post(message: str, image_bytes: bytes):
    text = preserve_new_lines(message)
    mastodon = Mastodon(
        access_token=mastodon_access_token,
        api_base_url=mastodon_api_base_url)
    if image_bytes:
        mastodon_upload_response = mastodon.media_post(
            media_file=BytesIO(image_bytes),
            mime_type=conf_luftdaten_graph_mime_type)
        mastodon.status_post(
            status=text,
            media_ids=[mastodon_upload_response])
    else:
        mastodon.status_post(
            status=text)


def preserve_new_lines(text):
    lines = text.split('\n')
    preserved_lines = [line if line.strip() else ' ' for line in lines]
    return '\n'.join(preserved_lines).rstrip()
