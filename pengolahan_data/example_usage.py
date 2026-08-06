"""
Contoh penggunaan modul ElasticsearchScanner dan crawling data per-platform secara langsung di Python.
"""
import pandas as pd
from config import load_env_config, DEFAULT_SOURCE_FIELDS
from es_scanner import ElasticsearchScanner

def main():
    # 1. Muat konfigurasi dari .env
    config = load_env_config()
    print(f"Connecting to ES: {config['base_url']} | Index: {config['index']}")

    # 2. Inisialisasi Scanner
    scanner = ElasticsearchScanner(
        host=config["host"],
        port=config["port"],
        index=config["index"],
        user=config["user"],
        password=config["password"]
    )

    # 3. Contoh Scan Streaming dokumen Twitter (misal 10 data)
    print("\n--- Streaming 10 dokumen Twitter ---")
    twitter_docs = []
    for doc in scanner.scan(platform="twitter", limit=10):
        twitter_docs.append(doc)
        print(f"ID: {doc.get('id')} | User: @{doc.get('username')} | Likes: {doc.get('likes_count')}")

    # 4. Contoh convert hasil scan ke Pandas DataFrame
    df_twitter = pd.DataFrame(twitter_docs)
    print("\n--- Contoh DataFrame ---")
    print(df_twitter[["id", "platform", "username", "likes_count", "reply_count", "shares_count"]].head())

    # 5. Contoh cek total dokumen untuk setiap platform di index
    print("\n--- Total dokumen per platform di index ---")
    platforms = ["twitter", "instagram", "tiktok", "youtube", "threads", "facebook"]
    for p in platforms:
        cnt = scanner.get_count(platform=p)
        print(f"Platform: {p:<10} | Estimasi Dokumen: {cnt:,}" if cnt is not None else f"Platform: {p:<10} | N/A")

if __name__ == "__main__":
    main()
