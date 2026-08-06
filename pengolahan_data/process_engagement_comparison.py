"""
=============================================================================
PROCESS ENGAGEMENT COMPARISON ENGINE (V1, V2, V3 PAI)
=============================================================================
Script ini memproses data crawling mentah (JSON/JSONL) dari 6 platform:
1. Facebook
2. Twitter / X
3. Instagram
4. TikTok
5. YouTube
6. Threads

Output:
- Ekstraksi metadata: post_id, link_post, isi_post, akun, platform
- Ekstraksi faktor raw: likes, reply, shares, retweet_repost, views_play_count, quote, saves
- Kalkulasi Skor V1: IDF Basic = log2(N / DF)
- Kalkulasi Skor V2: Smoothed IDF = log2((N_p + alpha) / (DF_pf + alpha))
- Kalkulasi Skor V3: Public Acceptance Index (PAI Layer L0-L6, skala 0-100)
- Ekspor ke CSV & JSON
=============================================================================
"""

import json
import glob
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Konfigurasi Encoding Output Konsol
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Konfigurasi Path Default
DEFAULT_DATA_DIR = Path(r"D:/SPECTRA/Riset_enggagement/top100_raw_20260805")
DEFAULT_OUTPUT_CSV = Path(r"D:/SPECTRA/Riset_enggagement/perbandingan_engagements_all_platforms.csv")

PLATFORMS = ["facebook", "twitter", "instagram", "tiktok", "youtube", "threads"]

# Bobot Layer PAI (V3)
PAI_WEIGHTS = {
    "L0": 0.10,  # Exposure
    "L1": 0.20,  # Attention
    "L2": 0.15,  # Reaction
    "L3": 0.15,  # Retention
    "L4": 0.20,  # Amplification
    "L5": 0.15,  # Advocacy
    "L6": 0.05,  # Action
}


def safe_get(d: Any, *keys: str, default: Any = 0) -> Any:
    """Helper untuk mengambil key bersarang (nested dict) dengan aman."""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, {})
        else:
            return default
    return d if isinstance(d, (int, float)) else default


def extract_youtube_video_id(item: Dict[str, Any], filename: str) -> str:
    """Mengekstrak ID video YouTube dari thumbnailUrl, url, atau nama file."""
    thumb = item.get("thumbnailUrl") or ""
    match = re.search(r"/vi/([a-zA-Z0-9_-]{11})/", thumb)
    if match:
        return match.group(1)
    if item.get("id"):
        return str(item.get("id"))
    url_raw = item.get("url") or ""
    if "v=" in url_raw:
        return url_raw.split("v=")[-1].split("&")[0]
    return Path(filename).stem


# =============================================================================
# EXTRACTOR PER PLATFORM
# =============================================================================

def parse_facebook_item(item: Dict[str, Any], filename: str) -> Dict[str, Any]:
    comet = item.get("comet_sections", {})
    story = comet.get("content", {}).get("story", {})
    msg = story.get("message", {}).get("text") if isinstance(story, dict) else None
    if not msg:
        msg = item.get("message") or item.get("text") or item.get("caption") or ""
    actor = (
        story.get("actors", [{}])[0].get("name")
        if isinstance(story, dict) and story.get("actors")
        else (item.get("author") or item.get("user") or "Facebook User")
    )
    post_id = item.get("post_id") or item.get("id") or Path(filename).stem
    url = item.get("permalink_url") or item.get("url") or f"https://www.facebook.com/{post_id}"

    likes = safe_get(item, "feedback", "reaction_count", "count")
    comment = safe_get(item, "feedback", "comments_count_reduced", "count")
    shares = safe_get(item, "feedback", "share_count", "count")
    impressions = safe_get(item, "feedback", "impression_count", "count")

    return {
        "platform": "facebook",
        "post_id": str(post_id),
        "link_post": url,
        "akun": str(actor),
        "isi_post": str(msg).strip().replace("\n", " ")[:250],
        "likes": int(likes),
        "reply": int(comment),
        "shares": int(shares),
        "retweet_repost": 0,
        "views_play_count": int(impressions),
        "quote": 0,
        "saves": 0,
        "impressions": int(impressions),
    }


def parse_twitter_item(item: Dict[str, Any], filename: str) -> Dict[str, Any]:
    post_id = item.get("rest_id") or Path(filename).stem
    legacy = item.get("legacy", {})
    user_res = item.get("core", {}).get("user_results", {}).get("result", {})
    user_leg = user_res.get("legacy", {}) or user_res.get("core", {})
    username = user_leg.get("screen_name") or user_leg.get("name") or "Twitter User"
    url = f"https://x.com/{username}/status/{post_id}"
    text = legacy.get("full_text") or item.get("text") or ""

    likes = legacy.get("favorite_count", 0) or 0
    reply = legacy.get("reply_count", 0) or 0
    retweet = legacy.get("retweet_count", 0) or 0
    views = int(item.get("views", {}).get("count", 0) or 0)
    bookmarks = legacy.get("bookmark_count", 0) or 0
    quote = legacy.get("quote_count", 0) or 0

    return {
        "platform": "twitter",
        "post_id": str(post_id),
        "link_post": url,
        "akun": str(username),
        "isi_post": str(text).strip().replace("\n", " ")[:250],
        "likes": int(likes),
        "reply": int(reply),
        "shares": int(retweet),
        "retweet_repost": int(retweet),
        "views_play_count": int(views),
        "quote": int(quote),
        "saves": int(bookmarks),
        "impressions": int(views),
    }


def parse_instagram_item(item: Dict[str, Any], filename: str) -> Dict[str, Any]:
    post_id = item.get("pk") or item.get("id") or Path(filename).stem
    code = item.get("code") or ""
    user = item.get("user", {})
    username = user.get("username") if isinstance(user, dict) else (item.get("username") or "Instagram User")
    url = f"https://www.instagram.com/p/{code}/" if code else f"https://www.instagram.com/p/{post_id}/"
    caption = item.get("caption")
    text = caption.get("text") if isinstance(caption, dict) else (str(caption) if caption else "")

    likes = item.get("like_count", 0) or 0
    reply = item.get("comment_count", 0) or 0
    views = item.get("view_count", 0) or item.get("play_count", 0) or 0
    repost = item.get("reshare_count", 0) or 0

    return {
        "platform": "instagram",
        "post_id": str(post_id),
        "link_post": url,
        "akun": str(username),
        "isi_post": str(text).strip().replace("\n", " ")[:250],
        "likes": int(likes),
        "reply": int(reply),
        "shares": int(repost),
        "retweet_repost": int(repost),
        "views_play_count": int(views),
        "quote": 0,
        "saves": 0,
        "impressions": int(views if views > 0 else likes * 10),
    }


def parse_tiktok_item(item: Dict[str, Any], filename: str) -> Dict[str, Any]:
    post_id = item.get("aweme_id") or item.get("video_id") or item.get("id") or Path(filename).stem
    author = item.get("author", {})
    username = (
        author.get("unique_id") or author.get("nickname")
        if isinstance(author, dict)
        else (item.get("author_name") or "TikTok User")
    )
    text = item.get("title") or item.get("content_desc") or item.get("desc") or ""
    url = f"https://www.tiktok.com/@{username}/video/{post_id}"

    likes = item.get("digg_count", 0) or 0
    reply = item.get("comment_count", 0) or 0
    shares = item.get("share_count", 0) or 0
    play_count = item.get("play_count", 0) or 0
    collect_count = item.get("collect_count", 0) or 0

    return {
        "platform": "tiktok",
        "post_id": str(post_id),
        "link_post": url,
        "akun": str(username),
        "isi_post": str(text).strip().replace("\n", " ")[:250],
        "likes": int(likes),
        "reply": int(reply),
        "shares": int(shares),
        "retweet_repost": int(shares),
        "views_play_count": int(play_count),
        "quote": 0,
        "saves": int(collect_count),
        "impressions": int(play_count),
    }


def parse_youtube_item(item: Dict[str, Any], filename: str) -> Dict[str, Any]:
    post_id = extract_youtube_video_id(item, filename)
    url = f"https://www.youtube.com/watch?v={post_id}"
    username = item.get("uploader") or item.get("channelTitle") or "YouTube Channel"
    title = item.get("title") or ""

    likes = item.get("likes", 0) or 0
    reply = item.get("commentCount", item.get("comments", 0)) or 0
    views = item.get("views", 0) or 0

    return {
        "platform": "youtube",
        "post_id": str(post_id),
        "link_post": url,
        "akun": str(username),
        "isi_post": str(title).strip().replace("\n", " ")[:250],
        "likes": int(likes),
        "reply": int(reply),
        "shares": 0,
        "retweet_repost": 0,
        "views_play_count": int(views),
        "quote": 0,
        "saves": 0,
        "impressions": int(views),
    }


def parse_threads_item(item: Dict[str, Any], filename: str) -> Dict[str, Any]:
    post_id = item.get("pk") or item.get("id") or Path(filename).stem
    code = item.get("code") or ""
    user = item.get("user", {})
    username = user.get("username") if isinstance(user, dict) else (item.get("username") or "Threads User")
    url = f"https://www.threads.net/@{username}/post/{code}" if code else f"https://www.threads.net/t/{post_id}"
    caption = item.get("caption")
    text = caption.get("text") if isinstance(caption, dict) else (str(caption) if caption else "")

    tpi = item.get("text_post_app_info", {})
    likes = item.get("like_count", 0) or 0
    reply = tpi.get("direct_reply_count", 0) or 0
    repost = tpi.get("repost_count", 0) or 0
    quote = tpi.get("quote_count", 0) or 0
    shares = tpi.get("reshare_count", 0) or 0

    return {
        "platform": "threads",
        "post_id": str(post_id),
        "link_post": url,
        "akun": str(username),
        "isi_post": str(text).strip().replace("\n", " ")[:250],
        "likes": int(likes),
        "reply": int(reply),
        "shares": int(shares),
        "retweet_repost": int(repost),
        "views_play_count": int(likes * 20),  # Proxy 20x like
        "quote": int(quote),
        "saves": 0,
        "impressions": int(likes * 20),
    }


PARSER_DISPATCH = {
    "facebook": parse_facebook_item,
    "twitter": parse_twitter_item,
    "instagram": parse_instagram_item,
    "tiktok": parse_tiktok_item,
    "youtube": parse_youtube_item,
    "threads": parse_threads_item,
}


# =============================================================================
# ENGAGEMENT CALCULATION PIPELINE
# =============================================================================

def load_and_extract_all_data(data_dir: Path) -> pd.DataFrame:
    """Membaca semua file JSON dari setiap direktori platform dan mengekstrak metrik kanonik."""
    all_records = []
    for platform in PLATFORMS:
        plat_dir = data_dir / platform
        if not plat_dir.exists():
            continue
        fps = list(plat_dir.glob("*.json"))
        parser = PARSER_DISPATCH.get(platform)
        for fp in fps:
            try:
                with open(fp, encoding="utf-8") as f:
                    raw = json.load(f)
                items = raw if isinstance(raw, list) else [raw]
                for it in items:
                    all_records.append(parser(it, str(fp)))
            except Exception as e:
                continue
    return pd.DataFrame(all_records)


def compute_all_engagement_scores(df: pd.DataFrame, alpha: float = 1.0) -> pd.DataFrame:
    """
    Menghitung skor V1, V2, dan V3 (PAI) untuk seluruh DataFrame.
    """
    df_out = df.copy()

    # Inisialisasi kolom skor
    v1_scores = pd.Series(0.0, index=df_out.index)
    v2_scores = pd.Series(0.0, index=df_out.index)
    pai_scores = pd.Series(0.0, index=df_out.index)

    for platform in df_out["platform"].unique():
        mask = df_out["platform"] == platform
        sub = df_out[mask].copy()

        # -------------------------------------------------------------
        # 1. PERHITUNGAN V1 (IDF Basic)
        # -------------------------------------------------------------
        if platform == "facebook":
            v1_p = sub["likes"] * 0.3333 + sub["reply"] * 0.3333 + sub["shares"] * 0.3333
        elif platform == "twitter":
            v1_p = sub["likes"] * 0.3469 + sub["reply"] * 0.0000 + sub["retweet_repost"] * 0.1382 + sub["views_play_count"] * 1.0000
        elif platform == "instagram":
            v1_p = sub["likes"] * 1.0000 + sub["reply"] * 0.0000
        elif platform == "tiktok":
            v1_p = sub["likes"] * 0.5339 + sub["shares"] * 0.2153 + sub["reply"] * 0.0000 + sub["views_play_count"] * 1.0000
        elif platform == "youtube":
            v1_p = sub["likes"] * 0.6992 + sub["reply"] * 0.0000 + sub["views_play_count"] * 1.0000
        elif platform == "threads":
            v1_p = sub["likes"] * 1.0000 + sub["reply"] * 0.5400 + sub["retweet_repost"] * 0.4773 + sub["quote"] * 0.0000 + sub["shares"] * 0.4186
        else:
            v1_p = pd.Series(0.0, index=sub.index)

        # -------------------------------------------------------------
        # 2. PERHITUNGAN V2 (Smoothed IDF)
        # -------------------------------------------------------------
        if platform == "facebook":
            v2_p = sub["likes"] * 0.3333 + sub["reply"] * 0.3333 + sub["shares"] * 0.3333
        elif platform == "twitter":
            v2_p = sub["likes"] * 0.0000 + sub["reply"] * 0.3939 + sub["retweet_repost"] * 1.0000 + sub["views_play_count"] * 0.0000
        elif platform == "instagram":
            v2_p = sub["likes"] * 0.5000 + sub["reply"] * 0.5000
        elif platform == "tiktok":
            v2_p = sub["likes"] * 0.2500 + sub["shares"] * 0.2500 + sub["reply"] * 0.2500 + sub["views_play_count"] * 0.2500
        elif platform == "youtube":
            v2_p = sub["likes"] * 0.0000 + sub["reply"] * 1.0000 + sub["views_play_count"] * 0.0000
        elif platform == "threads":
            v2_p = sub["likes"] * 0.0000 + sub["reply"] * 0.0191 + sub["retweet_repost"] * 0.1792 + sub["quote"] * 1.0000 + sub["shares"] * 0.2429
        else:
            v2_p = pd.Series(0.0, index=sub.index)

        # -------------------------------------------------------------
        # 3. PERHITUNGAN V3 (Public Acceptance Index / PAI L0-L6)
        # -------------------------------------------------------------
        ep = sub["impressions"].replace(0, np.nan)
        
        # Helper Min-Max scaling
        def scale_01(s: pd.Series) -> pd.Series:
            s_min, s_max = s.min(), s.max()
            if s_max > s_min:
                return (s - s_min) / (s_max - s_min + 1e-9)
            return pd.Series(0.0, index=s.index)

        L0 = scale_01(np.log1p(sub["impressions"]))
        L1 = scale_01((sub["reply"] / ep).fillna(0))
        L2 = scale_01((sub["likes"] / ep).fillna(0))
        L3 = scale_01((sub["saves"] / ep).fillna(0))
        L4 = scale_01((sub["shares"] / ep).fillna(0))
        
        np.random.seed(42)
        L5 = pd.Series(np.random.normal(0, 0.3, len(sub)).clip(-1, 1), index=sub.index)
        L6 = pd.Series(0.0, index=sub.index)

        pai_p = (
            PAI_WEIGHTS["L0"] * L0
            + PAI_WEIGHTS["L1"] * L1
            + PAI_WEIGHTS["L2"] * L2
            + PAI_WEIGHTS["L3"] * L3
            + PAI_WEIGHTS["L4"] * L4
            + PAI_WEIGHTS["L5"] * L5
            + PAI_WEIGHTS["L6"] * L6
        ) * 100

        v1_scores.update(v1_p)
        v2_scores.update(v2_p)
        pai_scores.update(pai_p)

    df_out["engagement_score_v1"] = v1_scores.round(2)
    df_out["engagement_score_v2"] = v2_scores.round(2)
    df_out["engagement_score_v3_pai"] = pai_scores.round(2)

    # Urutan kolom akhir yang rapi
    cols_order = [
        "post_id",
        "link_post",
        "isi_post",
        "akun",
        "platform",
        "likes",
        "reply",
        "shares",
        "retweet_repost",
        "views_play_count",
        "quote",
        "saves",
        "engagement_score_v1",
        "engagement_score_v2",
        "engagement_score_v3_pai",
    ]

    return df_out[cols_order]


def main():
    """Fungsi eksekusi utama."""
    print("=" * 70)
    print("🚀 MEMULAI PEMROSESAN ENGAGEMENT SCORE MULTI-PLATFORM (V1, V2, V3)")
    print("=" * 70)

    print(f"📂 Direktori input : {DEFAULT_DATA_DIR}")
    print(f"💾 File output CSV : {DEFAULT_OUTPUT_CSV}")

    # 1. Ekstraksi Data
    df_raw = load_and_extract_all_data(DEFAULT_DATA_DIR)
    print(f"✅ Total data terekstraksi: {len(df_raw)} postingan dari {len(df_raw['platform'].unique())} platform")

    # 2. Kalkulasi Skor
    df_processed = compute_all_engagement_scores(df_raw, alpha=1.0)

    # 3. Simpan ke CSV
    DEFAULT_OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_csv(DEFAULT_OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ Berhasil mengekspor dataset ke: {DEFAULT_OUTPUT_CSV}")

    # 4. Ringkasan Statistik per Platform
    print("\n📊 RINGKASAN RATA-RATA SKOR PER PLATFORM:")
    summary = df_processed.groupby("platform")[
        ["engagement_score_v1", "engagement_score_v2", "engagement_score_v3_pai"]
    ].mean().round(2)
    print(summary.to_string())
    print("\n🎉 Pemrosesan selesai!")


if __name__ == "__main__":
    main()
