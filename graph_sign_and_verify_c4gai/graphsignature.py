"""Graph signature"""

import hashlib
import logging
from datetime import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from rdflib import BNode, Graph
from rdflib.term import Node

logger = logging.getLogger(__name__)

blank_id: dict[Node, Graph] = {}
non_normalized: set[Node] = set()  # Set of non-normalized RdfValue objects

max_run_time = 1000  # Example max run time in milliseconds (set appropriately)
start_time = time()  # Used to track the runtime


def canonicalize_rdf(graph: Graph) -> str:
    """Step 1: Canonicalize the RDF Graph"""
    # Search for blanks
    find_blank_nodes(graph)

    # Serialize the graph to N-Triples
    serialized_graph = graph.serialize(format="nt")
    # Sort the triples for consistent ordering
    sorted_triples = sorted(serialized_graph.splitlines())
    # Join sorted triples back into a single string
    return "\n".join(sorted_triples)


def find_blank_nodes(graph: Graph) -> None:
    """Find blank nodes in the RDF Graph"""
    for s, p, o in graph.triples((None, None, None)):
        if isinstance(s, BNode):
            bgraph = blank_id.setdefault(s, Graph())
            bgraph.add((s, p, o))
        if isinstance(o, BNode):
            bgraph = blank_id.setdefault(s, Graph())
            bgraph.add((s, p, o))

    for bg in blank_id:
        logger.debug(bg)


def hash_rdf(canonicalized_graph: str) -> bytes:
    """Step 2: Hash the Canonicalized RDF Graph"""
    return hashlib.sha256(canonicalized_graph.encode("utf-8")).digest()


def generate_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
    """Step 3: Generate a private and public key pair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def sign_hash(private_key: RSAPrivateKey, rdf_hash: bytes) -> bytes:
    """Step 4: Sign the RDF Hash"""
    return private_key.sign(
        rdf_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verify_signature(public_key: RSAPublicKey, rdf_hash: bytes, signature: bytes) -> bool:
    """Step 5: Verify the Signature"""
    try:
        public_key.verify(
            signature,
            rdf_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except InvalidSignature:
        return False
    else:
        return True
