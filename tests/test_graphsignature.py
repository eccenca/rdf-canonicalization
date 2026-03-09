"""Tests for graphsignature.py"""

from rdflib import Graph

from graph_sign_and_verify_c4gai.graphsignature import (
    canonicalize_rdf,
    generate_key_pair,
    hash_rdf,
    sign_hash,
    verify_signature,
)

SIMPLE_RDF = """
<http://example.org/subject> <http://example.org/predicate> "object" .
<http://example.org/subject> <http://example.org/other> <http://example.org/value> .
"""

SHA256_DIGEST_SIZE = 32
SIMPLE_RDF_TRIPLE_COUNT = 2


def make_graph(rdf: str = SIMPLE_RDF) -> Graph:
    """Parse N-Triples into an rdflib Graph."""
    g = Graph()
    g.parse(data=rdf, format="nt")
    return g


def test_canonicalize_rdf_returns_string() -> None:
    """canonicalize_rdf returns a non-empty string."""
    g = make_graph()
    result = canonicalize_rdf(g)
    assert isinstance(result, str)
    assert len(result) > 0


def test_canonicalize_rdf_is_sorted() -> None:
    """canonicalize_rdf returns triples in sorted order."""
    g = make_graph()
    result = canonicalize_rdf(g)
    lines = result.splitlines()
    assert lines == sorted(lines)


def test_canonicalize_rdf_is_deterministic() -> None:
    """Two identical graphs produce the same canonical form."""
    g1 = make_graph()
    g2 = make_graph()
    assert canonicalize_rdf(g1) == canonicalize_rdf(g2)


def test_hash_rdf_returns_bytes() -> None:
    """hash_rdf returns a 32-byte SHA-256 digest."""
    canonical = canonicalize_rdf(make_graph())
    result = hash_rdf(canonical)
    assert isinstance(result, bytes)
    assert len(result) == SHA256_DIGEST_SIZE


def test_hash_rdf_is_deterministic() -> None:
    """hash_rdf returns the same digest for identical input."""
    canonical = canonicalize_rdf(make_graph())
    assert hash_rdf(canonical) == hash_rdf(canonical)


def test_hash_rdf_differs_for_different_input() -> None:
    """hash_rdf returns distinct digests for distinct inputs."""
    h1 = hash_rdf("graph1")
    h2 = hash_rdf("graph2")
    assert h1 != h2


def test_generate_key_pair_returns_keys() -> None:
    """generate_key_pair returns a non-None private and public key."""
    private_key, public_key = generate_key_pair()
    assert private_key is not None
    assert public_key is not None


def test_sign_and_verify_valid_signature() -> None:
    """A signature created with a private key verifies against the matching public key."""
    canonical = canonicalize_rdf(make_graph())
    rdf_hash = hash_rdf(canonical)
    private_key, public_key = generate_key_pair()
    signature = sign_hash(private_key, rdf_hash)
    assert verify_signature(public_key, rdf_hash, signature) is True


def test_verify_signature_invalid_with_wrong_hash() -> None:
    """Verifying a signature against a different hash returns False."""
    canonical = canonicalize_rdf(make_graph())
    rdf_hash = hash_rdf(canonical)
    private_key, public_key = generate_key_pair()
    signature = sign_hash(private_key, rdf_hash)

    wrong_hash = hash_rdf("different content")
    assert verify_signature(public_key, wrong_hash, signature) is False


def test_verify_signature_invalid_with_wrong_key() -> None:
    """Verifying a signature with a different key pair returns False."""
    canonical = canonicalize_rdf(make_graph())
    rdf_hash = hash_rdf(canonical)
    private_key, _ = generate_key_pair()
    signature = sign_hash(private_key, rdf_hash)

    _, other_public_key = generate_key_pair()
    assert verify_signature(other_public_key, rdf_hash, signature) is False


def test_sign_and_verify_empty_graph() -> None:
    """Sign/verify round-trip works for an empty graph."""
    g = Graph()
    canonical = canonicalize_rdf(g)
    rdf_hash = hash_rdf(canonical)
    private_key, public_key = generate_key_pair()
    signature = sign_hash(private_key, rdf_hash)
    assert verify_signature(public_key, rdf_hash, signature) is True


def test_canonicalize_rdf_with_serialization() -> None:
    """Reproduce the sign_example.py pattern: serialize to sorted N-Triples."""
    g = make_graph()
    canonical = canonicalize_rdf(g)
    lines = [line for line in canonical.splitlines() if line]
    assert len(lines) == SIMPLE_RDF_TRIPLE_COUNT
