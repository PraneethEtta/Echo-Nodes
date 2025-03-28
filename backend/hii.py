from pyvis.network import Network
import networkx as nx
from neo4j import GraphDatabase
from fastapi import APIRouter
from fastapi.responses import JSONResponse,HTMLResponse

graph_router = APIRouter()

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Inf0rmati0n@321"))

# Define colors for different node types
NODE_COLORS = {
    "Patient": "#a633ff",  # Purple
    "Problem": "#ff5733",  # Orange
    "Cause": "#33c4ff",    # Blue
    "Visit": "#ffcc33"     # Yellow
}

def fetch_graph(patient_id):
    query = f"""
        MATCH (p:Patient {{id: '{patient_id}'}})-[r1:HAS_PROBLEM]->(pr:Problem)
        OPTIONAL MATCH (pr)-[r2:HAS_CAUSE]->(c:Cause)
        OPTIONAL MATCH (p)-[r3:VISITED_ON]->(v:Visit)
        OPTIONAL MATCH (v)-[r4:FOR_PROBLEM]->(pr2:Problem)
        RETURN p, r1, pr, r2, c, r3, v, r4, pr2
    """
    with driver.session(database="neo4j") as session:
        graph = session.run(query, patient_id=patient_id).graph()


        G = nx.DiGraph()  # Use a directed graph for better structure

        # Add nodes with correct labels
        for node in graph.nodes:
            label = list(node.labels)[0]  # Get the first label (e.g., "Patient")
            color = NODE_COLORS.get(label, "#cccccc")  # Default to gray if unknown
            node_props = dict(node.items())

            # Assign meaningful labels
            if "Patient" in node.labels:
                node_label = node_props.get("name", "Unknown Patient")
            elif "Visit" in node.labels:
                node_label = node_props.get("date", "Unknown Date")
            elif "Problem" in node.labels:
                node_label = node_props.get("name", "Unknown Problem")
            elif "Cause" in node.labels:
                node_label = node_props.get("description", "Unknown Cause")
            else:
                node_label = label  # Default fallback

            title = str(node_props)  # Show properties on hover
            G.add_node(node.element_id, label=node_label, title=title, color=color, shape="dot")

        # Add edges
        for rel in graph.relationships:
            G.add_edge(
                rel.start_node.element_id, 
                rel.end_node.element_id, 
                title=rel.type, 
                label=rel.type, 
                color="gray"  # Keep relationships neutral
            )
        driver.close()
        return G

# Function to visualize graph using Pyvis
@graph_router.get("/generate-graph/{patient_id}")
def visualize_graph(patient_id):
    G=fetch_graph(patient_id)
    output_file = f"C:/Users/9901063/Downloads/Hackathon/frontend/public/{patient_id}.html"
    net = Network(notebook=True, directed=True)  # Make it a directed graph
    
    # Improve layout settings
    net.toggle_physics(True)  # Enable physics for better spacing
    net.repulsion(node_distance=200)  # Increase distance between nodes

    # Add nodes
    for node, data in G.nodes(data=True):
        net.add_node(node, label=data["label"], title=data["title"], color=data["color"], shape="dot")

    # Add edges
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, title=data["title"], label=data["label"], color=data["color"])

    # Save and show the graph
    net.show(output_file)
    
    with open(output_file, 'r') as file:
        html_content = file.read()

    return HTMLResponse(content=html_content)







