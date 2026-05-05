# reporter.py
# ─────────────────────────────────────────────
# Builds the HTML body for the daily portfolio
# email report. Charts are embedded via CID tags.
# ─────────────────────────────────────────────

from datetime import datetime


def generate_html_report(portfolio_data):
    """
    Accepts a list of portfolio data dicts and returns
    a formatted HTML string for the email body.
    Charts are referenced as cid:chart_<TICKER>.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;
                   max-width: 650px; margin: auto;">
        <h2 style="color: #2c3e50;"> Daily Portfolio Report — {date_str}</h2>

        <table border="1" cellpadding="10" cellspacing="0"
               style="border-collapse: collapse; width: 100%;">
          <tr style="background-color: #f2f2f2;">
            <th>Ticker</th>
            <th>Current Price</th>
            <th>Avg Cost</th>
            <th>Shares</th>
            <th>Total Value (USD)</th>
            <th>P/L (USD)</th>
            <th>Distance to Target</th>
          </tr>
    """

    target_hit = False

    for data in portfolio_data:
        ticker         = data['ticker']
        price          = data['price']
        cost           = data['avg_cost']
        shares         = data['shares']
        target         = data['target']
        total_val      = data['total_value']
        pl             = data['pl']
        pl_color       = "green" if pl >= 0 else "red"
        dist_to_target = round(target - price, 2)

        if ticker == "RDW" and price >= target:
            target_hit = True

        html += f"""
          <tr>
            <td><strong>{ticker}</strong></td>
            <td>${price}</td>
            <td>${cost}</td>
            <td>{shares}</td>
            <td>${total_val}</td>
            <td style="color: {pl_color}; font-weight: bold;">${pl}</td>
            <td>${dist_to_target} away</td>
          </tr>
        """

    html += "</table><br>"

    if target_hit:
        html += """
        <div style="background-color: #d4edda; color: #155724; padding: 15px;
                    border: 1px solid #c3e6cb; border-radius: 5px;
                    margin-bottom: 20px;">
            <h3 style="margin-top: 0;"> TARGET ACHIEVED! </h3>
            <p><strong>RDW has hit or exceeded your target of $13.71!</strong>
               Time to execute your plan.</p>
        </div>
        """

    html += "<h3 style='color: #2c3e50;'>Price Movement Charts</h3>"

    for data in portfolio_data:
        ticker = data['ticker']
        html += f"""
        <div style="margin-bottom: 30px;">
            <p style="margin-bottom: 6px;">
                <strong>{ticker}</strong> — Avg Cost:
                <span style="color: orange;">${data['avg_cost']}</span>
                &nbsp;|&nbsp;
                Target: <span style="color: green;">${data['target']}</span>
            </p>
            <img src="cid:chart_{ticker}"
                 alt="{ticker} Price Chart"
                 style="width: 100%; max-width: 620px; border: 1px solid #ddd;
                        border-radius: 6px; padding: 4px;" />
        </div>
        """

    html += """
        <p style="font-size: 0.85em; color: #7f8c8d; margin-top: 20px;">
            Data fetched via yfinance API &nbsp;|&nbsp;
            Logged to local SQLite DB &nbsp;|&nbsp;
            Chart reflects last 3 months of recorded closes &nbsp;|&nbsp;
            Projection is linear trend only — not financial advice
        </p>
      </body>
    </html>
    """
    return html
