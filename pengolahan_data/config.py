import os
from pathlib import Path
from dotenv import dotenv_values

# Path ke direktori saat ini
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

def load_env_config(env_file=ENV_PATH):
    """
    Membaca file .env dan mengembalikan konfigurasi koneksi Elasticsearch
    """
    config_dict = {}
    if Path(env_file).exists():
        config_dict = dotenv_values(env_file)

    # Fallback to os.environ if needed
    def get_val(key, default=None):
        return config_dict.get(key) or os.getenv(key, default)

    host = get_val("DB_HOST", "127.0.0.1")
    port = int(get_val("DB_PORT", 5200))
    user = get_val("DB_USER", None)
    password = get_val("DB_PASSWORD", None)
    index = get_val("index") or get_val("INDEX", "smm-data-hot-20260804")

    # Bersihkan kutipan jika ada
    if index:
        index = index.strip().strip("'\"")
    if host:
        host = host.strip().strip("'\"")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "index": index,
        "base_url": f"http://{host}:{port}"
    }

# Platform yang didukung
SUPPORTED_PLATFORMS = [
    "twitter",
    "instagram",
    "tiktok",
    "youtube",
    "threads",
    "facebook"
]

# Default Source Fields (dari query.txt)
DEFAULT_SOURCE_FIELDS = [
    "id",
    "platform",
    "content_type",
    "sub_type",
    "type",
    "text",
    "created_at",
    "hour",
    "dayname",
    "username",
    "user_id",
    "user_full_name",
    "user_description",
    "user_image",
    "user_followers_count",
    "user_followers_range",
    "range_follower",
    "user_friends_count",
    "user_statuses_count",
    "user_favourites_count",
    "user_created_at",
    "user_bot",
    "user_view_count",
    "likes_count",
    "reply_count",
    "shares_count",
    "views_count",
    "engagements",
    "watch_ratio",
    "score_post",
    "influence_count",
    "post_url",
    "llm_flag",
    "quoted_user_statuses_count",
    "quoted_user_friends_count",
    "quoted_user_followers_count",
    "retweeted_user_statuses_count",
    "retweeted_user_friends_count",
    "retweeted_user_followers_count",
    "repost_count",
    "quote_count",
    "dislike_count",
    "bookmark_count",
    "bookmarks_count",
    "save_count",
    "collect_count"
]
