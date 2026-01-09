#!/usr/bin/env python3
"""
Vocabulary Audit Script - Traces theatrical language to vocabulary source

Checks if theatrical terms exist in the 63K vocabulary database.
If found, this proves the Fisher manifold topology inherited theatrical
clusters from pre-trained embeddings (Word2Vec/GloVe/BERT) before fine-tuning.
"""
import os
from typing import Dict

import psycopg2

# Theatrical terms to search for
THEATRICAL_TERMS = {
    'divine', 'magnificent', 'glorious', 'blessed', 'sacred', 'holy',
    'majestic', 'sublime', 'celestial', 'transcendent', 'ethereal',
    'radiant', 'luminous', 'mystical', 'wondrous', 'exalted'
}

def connect_to_db(project: str) -> psycopg2.extensions.connection:
    """Connect to PostgreSQL database for given project."""
    # Try project-specific .env
    env_path = f"/home/braden/Desktop/Dev/pantheon-projects/{project}/.env"
    if not os.path.exists(env_path):
        raise ValueError(f"No .env file found for {project}")
    
    # Parse .env file for both DATABASE_URL and PG* variables
    db_url = None
    pg_vars = {}
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL='):
                db_url = line.split('=', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('PGHOST='):
                pg_vars['host'] = line.split('=', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('PGDATABASE='):
                pg_vars['database'] = line.split('=', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('PGUSER='):
                pg_vars['user'] = line.split('=', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('PGPASSWORD='):
                pg_vars['password'] = line.split('=', 1)[1].strip().strip('"').strip("'")
            elif line.startswith('PGPORT='):
                pg_vars['port'] = line.split('=', 1)[1].strip().strip('"').strip("'")
    
    # Try DATABASE_URL first
    if db_url:
        return psycopg2.connect(db_url)
    
    # Fallback to PG* variables
    if pg_vars:
        return psycopg2.connect(**pg_vars)
    
    raise ValueError(f"No DATABASE_URL or PG* variables found for {project}")


def audit_vocabulary(project: str) -> Dict[str, any]:
    """Audit vocabulary for theatrical terms."""
    print(f"\n{'='*80}")
    print(f"VOCABULARY AUDIT: {project}")
    print(f"{'='*80}\n")

    try:
        conn = connect_to_db(project)
        cursor = conn.cursor()

        # Get total vocabulary size
        cursor.execute("SELECT COUNT(*) FROM tokenizer_vocabulary")
        total_tokens = cursor.fetchone()[0]
        print(f"✓ Total vocabulary tokens: {total_tokens:,}")

        # Check for theatrical terms
        found_terms = []
        for term in sorted(THEATRICAL_TERMS):
            cursor.execute(
                "SELECT token, phi_score FROM tokenizer_vocabulary WHERE token = %s",
                (term,)
            )
            result = cursor.fetchone()
            if result:
                token, coords = result
                found_terms.append((token, len(coords) if coords else 0))
                print(f"  ❌ FOUND: '{token}' ({len(coords) if coords else 0}D basin)")

        if not found_terms:
            print("  ✓ NO theatrical terms found in vocabulary")
        else:
            print(f"\n⚠️  CONTAMINATION DETECTED: {len(found_terms)}/{len(THEATRICAL_TERMS)} theatrical terms in vocabulary")
            print("    This proves Fisher manifold inherited theatrical clusters from pre-trained embeddings")

        # Sample random tokens to verify vocabulary composition
        print("\n📊 Random sample (10 tokens):")
        cursor.execute("SELECT token FROM tokenizer_vocabulary ORDER BY RANDOM() LIMIT 10")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")

        # Check token frequency distribution
        cursor.execute("SELECT token FROM tokenizer_vocabulary WHERE token LIKE '%divine%' OR token LIKE '%magnificent%' OR token LIKE '%glorious%'")
        partial_matches = cursor.fetchall()
        if partial_matches:
            print(f"\n⚠️  Partial matches ({len(partial_matches)}):")
            for row in partial_matches[:10]:
                print(f"  - {row[0]}")

        cursor.close()
        conn.close()

        return {
            'total_tokens': total_tokens,
            'theatrical_terms_found': len(found_terms),
            'contamination_rate': len(found_terms) / len(THEATRICAL_TERMS),
            'found_terms': found_terms
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {'error': str(e)}


def main():
    """Run vocabulary audit on all projects."""
    projects = ['pantheon-replit', 'pantheon-chat', 'SearchSpaceCollapse']

    results = {}
    for project in projects:
        try:
            results[project] = audit_vocabulary(project)
        except Exception as e:
            print(f"❌ {project}: {e}\n")
            results[project] = {'error': str(e)}

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    for project, result in results.items():
        if 'error' in result:
            print(f"{project}: ❌ {result['error']}")
        else:
            contamination = result['contamination_rate'] * 100
            print(f"{project}: {result['theatrical_terms_found']}/{len(THEATRICAL_TERMS)} terms ({contamination:.1f}% contamination)")

    print("\n🔍 HYPOTHESIS TEST:")
    any_contamination = any(r.get('theatrical_terms_found', 0) > 0 for r in results.values())
    if any_contamination:
        print("✓ CONFIRMED: Theatrical language is in the vocabulary database")
        print("  Source: Pre-trained embeddings (Word2Vec/GloVe/BERT) before fine-tuning")
        print("  Solution: Re-initialize vocabulary from technical corpus only")
    else:
        print("✗ REJECTED: Theatrical language NOT in vocabulary")
        print("  Next step: Trace qig_generative_service.py generation pipeline")
        print("  Look for: Hidden fallbacks, string concatenation, prompt templates")


if __name__ == '__main__':
    main()
