"""Graph Signature Example usage"""
from datetime import time, datetime, date

from rdflib import Graph
import cryptography.hazmat.primitives.serialization as serialization
from graph_sign_and_verify_c4gai.graphsignature import (
    canonicalize_rdf,
    generate_key_pair,
    hash_rdf,
    sign_hash,
    verify_signature, start_time,
)

if __name__ == "__main__":
    file = "order-1.nt"

    # Create an RDF graph
    g = Graph()
    g.parse(file)

    # Canonicalize the graph
    canonical_graph = canonicalize_rdf(g)
    # canonicalize_rdf(g)
    print("Canonical Graph:\n", canonical_graph)

    # Hash the canonical graph
    rdf_hash = hash_rdf(canonical_graph)
    print("Hash:", rdf_hash.hex())
    with open(file + ".sha", "a") as f:
        f.write(rdf_hash.hex())
        f.write(" canonicalize_rdf\n")

    # Generate keys
    private_key, public_key = generate_key_pair()

    # Sign the hash
    signature = sign_hash(private_key, rdf_hash)
    print("Signature:", signature.hex())

    # Verify the signature
    is_valid = verify_signature(public_key, rdf_hash, signature)
    print("Signature valid:", is_valid)

    # Export public key (optional for external verification)
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    print("Public Key (PEM):\n", public_key_pem.decode("utf-8"))

    exit = time()
    duration = datetime.combine(date.today(), exit) - datetime.combine(date.today(), start_time)
    print("Time:\n", duration)
