# Stock Portfolio Tracker

A Python-based automated stock portfolio monitoring tool that fetches real-time market data,
stores historical price snapshots, and delivers a daily email summary — complete with
a performance chart — directly to your inbox every morning.

---

## Overview

This project was built to solve a real personal need: tracking the performance of a
live investment portfolio without manually checking prices every day.

The script runs automatically each morning, pulls the latest stock prices via the
**yfinance** API, logs the data to a local **SQLite** database, generates a
**Matplotlib performance chart** (spanning the most recent 3 months), and sends a
formatted **HTML email** with the chart attached to a configured gmail address.

---

## Tech Stack

| Component        | Tool / Library        |
|------------------|-----------------------|
| Language         | Python 3.x            |
| Market Data API  | yfinance              |
| Data Storage     | SQLite (via sqlite3)  |
| Data Processing  | Pandas                |
| Visualization    | Matplotlib            |
| Email Delivery   | smtplib + MIME        |
| Scheduler        | Windows Task Scheduler (runs daily on local laptop) |

---

## Features

- **Real-time price fetching** — pulls current stock prices using `yfinance`
- **Persistent local storage** — logs daily price snapshots to a SQLite database
- **Performance charting** — generates a line chart showing:
  - Each stock's initial cost basis
  - Price movements over the last 3 months
  - A projected trend line
- **Automated daily email** — sends a formatted HTML summary with the chart embedded
- **Portfolio holdings tracked:**
  - `UEC` — xxx amount for $$$
  - `RDW` — xxx amount for $$$

---

## Prerequisites

Make sure you have Python installed, then install the required libraries: requirements.txt
