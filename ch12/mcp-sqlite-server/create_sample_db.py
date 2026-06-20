import sqlite3

# Connect to a new (or existing) SQLite database.
conn = sqlite3.connect("startups.db")
cursor = conn.cursor()

# Create a table for startup funding information.
cursor.execute('''
CREATE TABLE IF NOT EXISTS startups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_name TEXT NOT NULL,
    description TEXT,
    website TEXT,
    funding_amount REAL,
    funding_date TEXT,
    investors TEXT
)
''')

# Insert some example records.
startups = [
    ("AlphaTech", "Innovative AI startup", "https://alphatech.io", 5_000_000, "2023-05-15", "Investor A, Investor B"),
    ("BetaSoft", "Enterprise SaaS solution", "https://betasoft.com", 12_000_000, "2023-06-20", "Investor C"),
    ("Gamma Innovations", "Cutting-edge biotech research", "https://gammainnovations.org", 7_500_000, "2023-07-10", "Investor D, Investor E, Investor F"),
    ("Delta Ventures", "Fintech disrupting traditional banking", "https://deltaventures.net", 20_000_000, "2023-08-25", "Investor G"),
    ("Epsilon Dynamics", "Sustainability through green energy", "https://epsilondynamics.com", 10_000_000, "2023-09-05", "Investor H, Investor I"),
]

cursor.executemany('''
    INSERT INTO startups (startup_name, description, website, funding_amount, funding_date, investors)
    VALUES (?, ?, ?, ?, ?, ?)
''', startups)

conn.commit()
conn.close()