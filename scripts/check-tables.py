#!/usr/bin/env python3
"""Check if learned_words table exists in databases"""
import psycopg2


def check_table_exists(db_name, connection_string):
    try:
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Check if learned_words table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'learned_words'
            );
        """)
        table_exists = cur.fetchone()[0]

        if table_exists:
            # Get row count
            cur.execute("SELECT COUNT(*) FROM learned_words;")
            row_count = cur.fetchone()[0]
            print(f"✅ {db_name}: learned_words table EXISTS with {row_count} rows")

            # Check vocabulary_observations
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'vocabulary_observations'
                );
            """)
            vocab_exists = cur.fetchone()[0]
            if vocab_exists:
                cur.execute("SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word';")
                vocab_count = cur.fetchone()[0]
                print(f"   📊 vocabulary_observations has {vocab_count} word entries")
        else:
            print(f"❌ {db_name}: learned_words table DOES NOT EXIST")

            # Check vocabulary_observations
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'vocabulary_observations'
                );
            """)
            vocab_exists = cur.fetchone()[0]
            if vocab_exists:
                cur.execute("SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word';")
                vocab_count = cur.fetchone()[0]
                print(f"   ✅ vocabulary_observations EXISTS with {vocab_count} word entries")
                print("   → Migration NOT needed - already using vocabulary_observations!")

        cur.close()
        conn.close()
        return table_exists

    except Exception as e:
        print(f"❌ {db_name}: Error - {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Checking vocabulary table status across projects")
    print("=" * 70)
    print()

    # pantheon-chat (Railway)
    pantheon_chat_url = "postgresql://postgres:4rgyvhmwjqbcez1a41nl4766a3w2lqu2@nozomi.proxy.rlwy.net:40463/railway"
    check_table_exists("pantheon-chat (Railway)", pantheon_chat_url)
    print()

    # SearchSpaceCollapse (Neon us-west-2)
    searchspace_url = "postgresql://neondb_owner:npg_hk3rWRIPJ6Ht@ep-still-dust-afuqyc6r.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
    check_table_exists("SearchSpaceCollapse (Neon)", searchspace_url)
    print()

    print("=" * 70)
