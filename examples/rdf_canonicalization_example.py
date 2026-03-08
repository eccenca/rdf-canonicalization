"""RDF Canonicalization Example usage"""
import rdflib
from rdflib import Graph
from graph_sign_and_verify_c4gai.graphsignature import hash_rdf
from graph_sign_and_verify_c4gai.rdf_canonicalization import RdfCanonicalization

if __name__ == "__main__":
    # file = "order-1.nt"
    file = "../tests/rdfc10/test023-in.nq"

    graph: Graph = rdflib.Graph()
    graph.parse(file, format="turtle")  # Replace with your RDF file path

    normalizer = RdfCanonicalization(graph, max_run_time=5)
    normalized_output = sorted(normalizer.normalize.splitlines())
    print("\n".join(normalized_output))

    # Hash the canonical graph
    rdf_hash = hash_rdf("\n".join(normalized_output))
    print("Hash:", rdf_hash.hex())
    with open(file + ".sha", "a") as f:
        f.write(rdf_hash.hex())
        f.write(" rdf_normalizer\n")
