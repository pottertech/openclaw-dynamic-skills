#!/usr/bin/env python3
"""
OpenClaw Dynamic Skills — Embedding Generator (Phase 2)

Generates pgvector embeddings for skills using local models.

Usage:
    python3 generate_embeddings.py [--all|--skill-id <id>]
    
Environment Variables:
    SKILLS_DB_DSN: PostgreSQL connection string
    EMBEDDING_MODEL: Model to use (default: sentence-transformers/all-MiniLM-L6-v2)
"""

import os
import sys
import hashlib
from typing import List, Optional

# Try to import dependencies
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("❌ psycopg2 not installed")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed")
    print("Install with: pip3 install sentence-transformers")
    sys.exit(1)

try:
    from xid import Xid
    XID_AVAILABLE = True
except ImportError:
    XID_AVAILABLE = False
    import uuid


# Configuration
DB_DSN = os.getenv('SKILLS_DB_DSN', 'postgresql://localhost:5432/skillsdb')
MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
BATCH_SIZE = 32


def generate_id() -> str:
    """Generate XID or UUID."""
    if XID_AVAILABLE:
        return str(Xid().string())
    return str(uuid.uuid4())


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(DB_DSN)


def load_model():
    """Load sentence transformer model."""
    print(f"📥 Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"✅ Model loaded (embedding dimension: {model.get_sentence_embedding_dimension()})")
    return model


def get_skills_without_embeddings(conn) -> List[dict]:
    """Get all skills that don't have embeddings yet."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, description, body
            FROM skills
            WHERE embedding IS NULL AND status = 'active'
            ORDER BY name
        """)
        return cur.fetchall()


def generate_embedding(model, text: str) -> List[float]:
    """Generate embedding vector for text."""
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def update_skill_embedding(conn, skill_id: str, embedding: List[float]):
    """Update skill with embedding vector."""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE skills
            SET embedding = %s
            WHERE id = %s
        """, (embedding, skill_id))
    conn.commit()


def generate_chunk_embeddings(conn, model):
    """Generate embeddings for skill chunks (for RAG)."""
    print("\n📝 Generating chunk embeddings...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get chunks without embeddings
        cur.execute("""
            SELECT sc.id, sc.chunk_text, s.name
            FROM skill_chunks sc
            JOIN skills s ON sc.skill_id = s.id
            WHERE sc.embedding IS NULL
            LIMIT 100
        """)
        chunks = cur.fetchall()
        
        if not chunks:
            print("✅ All chunks have embeddings")
            return
        
        print(f"   Found {len(chunks)} chunks to process")
        
        # Process in batches
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i+BATCH_SIZE]
            texts = [chunk['chunk_text'] for chunk in batch]
            
            # Generate embeddings for batch
            embeddings = model.encode(texts, convert_to_numpy=True)
            
            # Update each chunk
            for chunk, embedding in zip(batch, embeddings):
                cur.execute("""
                    UPDATE skill_chunks
                    SET embedding = %s
                    WHERE id = %s
                """, (embedding.tolist(), chunk['id']))
            
            conn.commit()
            print(f"   Processed {min(i+BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")
    
    print("✅ Chunk embeddings generated")


def create_chunks_for_skills(conn, model):
    """Create skill chunks for RAG (split body into ~500 char chunks)."""
    print("\n📝 Creating skill chunks...")
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get skills that don't have chunks yet
        cur.execute("""
            SELECT s.id, s.name, s.body
            FROM skills s
            WHERE NOT EXISTS (
                SELECT 1 FROM skill_chunks sc WHERE sc.skill_id = s.id
            )
            AND status = 'active'
        """)
        skills = cur.fetchall()
        
        if not skills:
            print("✅ All skills have chunks")
            return
        
        print(f"   Found {len(skills)} skills to chunk")
        
        for skill in skills:
            body = skill['body']
            skill_id = skill['id']
            
            # Split into chunks (~500 chars each)
            chunk_size = 500
            overlap = 50
            chunks = []
            
            for i in range(0, len(body), chunk_size - overlap):
                chunk_text = body[i:i+chunk_size]
                chunks.append({
                    'id': generate_id(),
                    'skill_id': skill_id,
                    'chunk_index': len(chunks),
                    'chunk_text': chunk_text
                })
            
            # Insert chunks
            for chunk in chunks:
                cur.execute("""
                    INSERT INTO skill_chunks (id, skill_id, chunk_index, chunk_text)
                    VALUES (%s, %s, %s, %s)
                """, (chunk['id'], chunk['skill_id'], chunk['chunk_index'], chunk['chunk_text']))
        
        conn.commit()
        print(f"✅ Created chunks for {len(skills)} skills")


def main():
    """Generate embeddings for all skills."""
    print("🧠 OpenClaw Dynamic Skills - Embedding Generator (Phase 2)")
    print("=" * 60)
    print("")
    
    # Load model
    model = load_model()
    print("")
    
    # Connect to database
    print(f"💾 Connecting to database...")
    conn = get_db_connection()
    print("✅ Connected")
    print("")
    
    # Step 1: Create chunks for skills
    create_chunks_for_skills(conn, model)
    
    # Step 2: Generate chunk embeddings
    generate_chunk_embeddings(conn, model)
    
    # Step 3: Generate skill-level embeddings
    print("\n📝 Generating skill embeddings...")
    skills = get_skills_without_embeddings(conn)
    
    if not skills:
        print("✅ All skills already have embeddings")
    else:
        print(f"   Found {len(skills)} skills to process")
        
        for i, skill in enumerate(skills, 1):
            # Create text for embedding (name + description + first 500 chars of body)
            text = f"{skill['name']} {skill['description']} {skill['body'][:500]}"
            
            # Generate embedding
            embedding = generate_embedding(model, text)
            
            # Update database
            update_skill_embedding(conn, skill['id'], embedding)
            
            print(f"   [{i}/{len(skills)}] {skill['name']}")
    
    conn.close()
    
    print("")
    print("=" * 60)
    print("✅ Embedding generation complete!")
    print("")
    print("Next steps:")
    print("  1. Update lookup_service.py to use semantic search")
    print("  2. Test semantic queries")
    print("  3. Compare with keyword search results")


if __name__ == '__main__':
    main()
