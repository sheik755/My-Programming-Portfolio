# main.py
# ─────────────────────────────────────────────
# Entry point for the daily portfolio tracker.
# Orchestrates: fetch → store → chart → email
# ─────────────────────────────────────────────

from datetime import datetime
from config     import PORTFOLIO
from fetcher    import get_latest_price
from storage    import init_db, insert_daily_record
from visualizer import generate_chart_bytes
from reporter   import generate_html_report
from emailer    import send_email


def main():
    print("Starting daily portfolio check...")
    conn     = init_db()
    cursor   = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")

    report_data = []

    for ticker, info in PORTFOLIO.items():
        price = get_latest_price(ticker)

        if price:
            total_value   = round(price * info['shares'], 2)
            total_cost    = round(info['avg_cost'] * info['shares'], 2)
            unrealized_pl = round(total_value - total_cost, 2)

            insert_daily_record(
                cursor, date_str, ticker, price,
                info['shares'], total_value, unrealized_pl
            )

            report_data.append({
                'ticker'     : ticker,
                'price'      : price,
                'avg_cost'   : info['avg_cost'],
                'shares'     : info['shares'],
                'target'     : info['target'],
                'total_value': total_value,
                'pl'         : unrealized_pl
            })
            print(f"{ticker}: ${price}")

    conn.commit()

    if report_data:
        chart_images = {}
        for data in report_data:
            ticker = data['ticker']
            print(f"Generating chart for {ticker}...")
            chart_images[ticker] = generate_chart_bytes(
                conn, ticker,
                data['avg_cost'],
                data['target']
            )

        conn.close()

        html_report = generate_html_report(report_data)
        send_email(
            f"Daily Portfolio Report: RDW & UEC — {date_str}",
            html_report,
            chart_images
        )
    else:
        conn.close()
        print("No data retrieved. Email not sent.")


if __name__ == "__main__":
    main()
