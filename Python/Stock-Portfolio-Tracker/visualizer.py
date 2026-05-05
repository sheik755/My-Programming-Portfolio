# visualizer.py
# ─────────────────────────────────────────────
# Generates price history charts (last 3 months)
# with a 30-day linear projection line.
# Returns raw PNG bytes for email embedding.
# ─────────────────────────────────────────────

import warnings
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from storage import get_price_history


def generate_chart_bytes(conn, ticker, avg_cost, target):
    """
    Builds a price chart for the given ticker using the last 3 months
    of recorded closes. Overlays avg cost, target, and a 30-day
    linear projection. Returns PNG bytes or None if insufficient data.
    """
    dates, prices = get_price_history(conn, ticker)

    if len(dates) < 1:
        return None

    # ── Filter to last 3 months ───────────────────────────────────
    today       = datetime.now()
    month_3_ago = today.month - 3

    if month_3_ago <= 0:
        three_months_ago = today.replace(
            year=today.year - 1, month=month_3_ago + 12
        )
    else:
        three_months_ago = today.replace(month=month_3_ago)

    filtered = [(d, p) for d, p in zip(dates, prices) if d >= three_months_ago]

    if len(filtered) == 0:
        filtered = list(zip(dates, prices))

    filtered_dates  = [f[0] for f in filtered]
    filtered_prices = [f[1] for f in filtered]

    # ── Linear Projection (30 days forward) ──────────────────────
    date_nums = np.array(
        [(d - filtered_dates[0]).days for d in filtered_dates], dtype=float
    )
    price_arr   = np.array(filtered_prices, dtype=float)
    proj_dates  = []
    proj_prices = []

    if len(date_nums) >= 3 and (date_nums[-1] - date_nums[0]) > 1:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                coeffs    = np.polyfit(date_nums, price_arr, 1)
                trend_fn  = np.poly1d(coeffs)
                last_day  = date_nums[-1]
                proj_days = np.linspace(last_day, last_day + 30, 30)
                proj_dates  = [
                    filtered_dates[0] + timedelta(days=int(d))
                    for d in proj_days
                ]
                proj_prices = trend_fn(proj_days)
        except Exception as e:
            print(f"Projection skipped for {ticker}: {e}")

    # ── Plot ──────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(filtered_dates, filtered_prices,
            marker='o', color='#2980b9', linewidth=2,
            markersize=5, label='Close Price')
    ax.fill_between(filtered_dates, filtered_prices,
                    alpha=0.1, color='#2980b9')

    if len(proj_dates) > 0:
        ax.plot(proj_dates, proj_prices,
                color='#8e44ad', linewidth=1.8,
                linestyle='--', label='Projected Trend (30d)')
        ax.fill_between(proj_dates, proj_prices,
                        alpha=0.07, color='#8e44ad')
        ax.annotate(
            f'  ~${round(float(proj_prices[-1]), 2)}',
            xy=(proj_dates[-1], proj_prices[-1]),
            fontsize=8, color='#8e44ad', va='center'
        )

    ax.axhline(y=avg_cost, color='orange', linestyle='--',
               linewidth=1.5, label=f'Avg Cost ${avg_cost}')
    ax.axhline(y=target, color='green', linestyle=':',
               linewidth=1.5, label=f'Target ${target}')
    ax.axvline(x=today, color='gray', linestyle=':',
               linewidth=1.2, label='Today')

    ax.set_title(f'{ticker} — Last 3 Months + 30-Day Projection',
                 fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Price (USD)', fontsize=10)
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, linestyle='--', alpha=0.4)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()

    # ── Save to bytes ─────────────────────────────────────────────
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=120)
    buffer.seek(0)
    png_bytes = buffer.read()
    plt.close(fig)

    return png_bytes
