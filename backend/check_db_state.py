"""Check current database state before regeneration."""
import pandas as pd
from sqlalchemy import create_engine
from app.core.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)

with engine.connect() as conn:
    tables = pd.read_sql(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name",
        conn
    )
    print("Tables:", tables['table_name'].tolist())

    for table in ['raw_cost_data', 'processed_cost_data']:
        try:
            count = pd.read_sql(f'SELECT COUNT(*) as cnt FROM {table}', conn)
            sample = pd.read_sql(f'SELECT * FROM {table} LIMIT 3', conn)
            print(f'\n{table}: {count["cnt"].iloc[0]} rows')
            print(f'Columns: {list(sample.columns)}')
        except Exception as e:
            print(f'\n{table}: ERROR - {e}')

    try:
        users = pd.read_sql('SELECT id, email FROM users LIMIT 5', conn)
        print(f'\nUsers: {len(users)} found')
        print(users.to_string())
    except Exception as e:
        print(f'Users: ERROR - {e}')
