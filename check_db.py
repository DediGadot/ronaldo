import sqlite3

def check_database():
    """Check the contents of the database and display statistics."""
    try:
        conn = sqlite3.connect('e28_parts.db')
        cursor = conn.cursor()

        # Get total count
        cursor.execute('SELECT COUNT(*) FROM parts')
        total_count = cursor.fetchone()[0]
        print(f"Total parts in database: {total_count}")

        # Get count by source
        cursor.execute('SELECT source, COUNT(*) FROM parts GROUP BY source')
        sources = cursor.fetchall()
        print("\nParts by source:")
        for source, count in sources:
            print(f"  {source}: {count}")

        # Get count by series
        cursor.execute('SELECT series, COUNT(*) FROM parts GROUP BY series')
        series = cursor.fetchall()
        print("\nParts by series:")
        for series_name, count in series:
            print(f"  {series_name}: {count}")

        # Show sample parts
        cursor.execute('SELECT id, title_en, source, series, price FROM parts LIMIT 5')
        sample_parts = cursor.fetchall()
        print("\nSample parts:")
        print("ID  | Title | Source | Series | Price")
        print("-" * 50)
        for part in sample_parts:
            print(f"{part[0]} | {part[1][:30]}... | {part[2]} | {part[3]} | ${part[4]}")

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()