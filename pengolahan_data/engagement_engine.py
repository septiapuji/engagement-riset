import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# Definisi Faktor per Platform berdasarkan Matriks Riset Terbaru
FACTORS_V1 = {
    "facebook": ["likes_count", "reply_count", "shares_count"],
    "twitter": ["likes_count", "reply_count", "shares_count"],
    "instagram": ["likes_count", "reply_count"],
    "tiktok": ["likes_count", "shares_count", "reply_count", "views_count"],
    "youtube": ["likes_count", "reply_count", "views_count"],  # Dislikes dropped
    "threads": ["likes_count", "reply_count", "repost_count", "quotes_count", "shares_count"],
}

FACTORS_V2 = {
    "facebook": ["shares_count", "likes_count", "reply_count"],
    "twitter": ["shares_count", "views_count", "reply_count", "likes_count", "quotes_count", "bookmark_count"],
    "instagram": ["shares_count", "reply_count", "likes_count", "repost_count"],
    "tiktok": ["shares_count", "views_count", "reply_count", "likes_count", "repost_count", "bookmark_count"],
    "youtube": ["shares_count", "views_count", "reply_count", "likes_count"],  # Dislikes dropped
    "threads": ["shares_count", "repost_count", "quotes_count", "reply_count", "likes_count"],
}


class EngagementEngine:
    """
    Engine perhitungan Engagement Score Invers Weight (V1 dan V2)
    sesuai dokumen riset 'dokumentasi_perhitungan/'.
    """

    def __init__(self, alpha: float = 1.0, timeframe_days: Optional[float] = None):
        """
        Args:
            alpha: Konstanta smoothing untuk V2 (default: 1.0)
            timeframe_days: Jumlah hari rentang data untuk V1 (jika None dihitung dari dataset)
        """
        self.alpha = alpha
        self.timeframe_days = timeframe_days

    def _determine_timeframe(self, df: pd.DataFrame) -> float:
        """Menentukan rentang waktu dataset dalam hari (Timeframe)"""
        if self.timeframe_days and self.timeframe_days > 0:
            return float(self.timeframe_days)

        if "created_at" in df.columns:
            ts = pd.to_datetime(df["created_at"], errors="coerce").dropna()
            if len(ts) >= 2:
                delta_days = (ts.max() - ts.min()).total_seconds() / (24 * 3600)
                if delta_days >= 1.0:
                    return delta_days
        return 1.0  # Default 1 hari jika data 1 hari atau tidak ada created_at

    def compute_weights_v1(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Menghitung bobot faktor global V1:
        IDF = log2(N / DF)
        - N = Rata-rata kemunculan faktor per hari = Jumlah Total Faktor / Timeframe (day)
        - DF = Total Post keseluruhan dalam Timeframe
        """
        timeframe = self._determine_timeframe(df)
        total_posts = max(len(df), 1)

        weights_v1: Dict[str, float] = {}
        all_factors = set()
        for f_list in FACTORS_V1.values():
            all_factors.update(f_list)

        for factor in all_factors:
            if factor in df.columns:
                total_factor_val = df[factor].fillna(0).sum()
                # N = rata-rata per hari
                n_val = total_factor_val / timeframe
                
                # Formula V1: IDF = log2(N / DF)
                if n_val > 0 and total_posts > 0:
                    ratio = n_val / total_posts
                    if ratio > 0:
                        idf = math.log2(ratio)
                    else:
                        idf = 0.0
                else:
                    idf = 0.0
                weights_v1[factor] = idf
            else:
                weights_v1[factor] = 0.0

        return weights_v1

    def compute_weights_v2(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Menghitung bobot faktor per-platform V2:
        IDF_p,f = log2((N_p + alpha) / (DF_p,f + alpha))
        - N_p = Total post di platform p
        - DF_p,f = Jumlah post di platform p dengan nilai faktor f > 0
        - alpha = Konstanta smoothing
        """
        weights_v2: Dict[str, Dict[str, float]] = {}

        for platform, factors in FACTORS_V2.items():
            df_p = df[df["platform"].str.lower() == platform.lower()]
            n_p = len(df_p)
            weights_v2[platform] = {}

            for factor in factors:
                if n_p == 0 or factor not in df.columns:
                    weights_v2[platform][factor] = 0.0
                    continue

                # DF_p,f = Banyaknya postingan di platform p yang memiliki faktor f > 0
                df_pf = (df_p[factor].fillna(0) > 0).sum()

                # Formula V2: log2((N_p + alpha) / (DF_p,f + alpha))
                numerator = n_p + self.alpha
                denominator = df_pf + self.alpha
                
                idf_pf = math.log2(numerator / denominator)

                # Clamping agar tidak negatif
                idf_pf = max(0.0, idf_pf)
                weights_v2[platform][factor] = round(idf_pf, 6)

        return weights_v2

    def calculate_scores(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Menghitung skor engagement V1 dan V2 untuk setiap baris postingan di DataFrame.
        
        Returns:
            Tuple (DataFrame dengan kolom skor baru, Dict ringkasan bobot & statistik)
        """
        if df.empty:
            return df, {}

        df_result = df.copy()

        # 1. Hitung bobot V1 dan V2
        weights_v1 = self.compute_weights_v1(df_result)
        weights_v2 = self.compute_weights_v2(df_result)

        # 2. Hitung Skor V1 untuk tiap baris
        scores_v1 = []
        for _, row in df_result.iterrows():
            platform = str(row.get("platform", "")).lower()
            factors = FACTORS_V1.get(platform, [])
            score = 0.0
            for f in factors:
                val = row.get(f, 0)
                if pd.notna(val) and val > 0:
                    w = weights_v1.get(f, 0.0)
                    score += float(val) * w
            scores_v1.append(score)

        # 3. Hitung Skor V2 untuk tiap baris
        scores_v2 = []
        for _, row in df_result.iterrows():
            platform = str(row.get("platform", "")).lower()
            factors = FACTORS_V2.get(platform, [])
            platform_weights = weights_v2.get(platform, {})
            score = 0.0
            for f in factors:
                val = row.get(f, 0)
                if pd.notna(val) and val > 0:
                    w = platform_weights.get(f, 0.0)
                    score += float(val) * w
            scores_v2.append(score)

        df_result["engagement_score_v1"] = scores_v1
        df_result["engagement_score_v2"] = scores_v2

        # 4. Tambahan Normalisasi Log Scale (Sesuai Rekomendasi Riset)
        df_result["engagement_score_v2_log"] = np.log1p(np.maximum(0, scores_v2))

        # Ringkasan Metadata
        summary = {
            "total_documents": len(df_result),
            "timeframe_days": round(self._determine_timeframe(df_result), 2),
            "alpha_v2": self.alpha,
            "weights_v1": weights_v1,
            "weights_v2": weights_v2,
            "platform_stats": {}
        }

        for p in df_result["platform"].unique():
            p_str = str(p).lower()
            sub = df_result[df_result["platform"].str.lower() == p_str]
            summary["platform_stats"][p_str] = {
                "count": len(sub),
                "avg_score_v1": round(float(sub["engagement_score_v1"].mean()), 4),
                "avg_score_v2": round(float(sub["engagement_score_v2"].mean()), 4),
                "max_score_v2": round(float(sub["engagement_score_v2"].max()), 4),
                "min_score_v2": round(float(sub["engagement_score_v2"].min()), 4),
            }

        return df_result, summary


def generate_engagement_report(df_scored: pd.DataFrame, summary: Dict[str, Any]) -> str:
    """Membuat laporan teks/tabel ringkas perbandingan bobot dan performa skor"""
    lines = []
    lines.append("=" * 75)
    lines.append("📈 LAPORAN PERHITUNGAN ENGAGEMENT SCORE (V1 vs V2)")
    lines.append("=" * 75)
    lines.append(f"Total Dokumen: {summary.get('total_documents', 0):,} | Timeframe: {summary.get('timeframe_days', 1)} hari | Alpha Smoothing (V2): {summary.get('alpha_v2', 1.0)}")
    lines.append("-" * 75)

    lines.append("\n⚖️ TABEL BOBOT FAKTOR V2 (IDF_p,f per Platform):")
    lines.append(f"{'Platform':<12} | {'Faktor':<15} | {'Bobot IDF V2':<12}")
    lines.append("-" * 45)
    weights_v2 = summary.get("weights_v2", {})
    for platform, factors in weights_v2.items():
        for factor, weight in factors.items():
            lines.append(f"{platform:<12} | {factor:<15} | {weight:<12.4f}")

    lines.append("\n📊 STATISTIK ENGAGEMENT SCORE PER PLATFORM:")
    lines.append(f"{'Platform':<12} | {'Total Post':<10} | {'Mean Score V1':<14} | {'Mean Score V2':<14} | {'Max Score V2':<12}")
    lines.append("-" * 75)
    p_stats = summary.get("platform_stats", {})
    for p, st in p_stats.items():
        lines.append(f"{p:<12} | {st['count']:<10,d} | {st['avg_score_v1']:<14.4f} | {st['avg_score_v2']:<14.4f} | {st['max_score_v2']:<12.4f}")

    lines.append("=" * 75)
    return "\n".join(lines)
