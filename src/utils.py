import re




# Function to validate YouTube URLs
def is_valid_youtube_url(url):
    pattern = r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}($|[&?])'
    return re.match(pattern, url) is not None

# Function to format timestamps in MM:SS format
def format_timestamp(seconds):
    hours, minutes, secs = divmod(int(seconds), 60, 60)
    return f"{minutes}:{secs:02d}"