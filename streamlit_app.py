import streamlit as st
from neo4j import GraphDatabase
import sys
sys.path.append('/home/ubuntu/Scrapegraph-ai')  # Ensure scraper.py is findable
from scraper import scrape_url  # Import the scrape_url function

# Neo4j connection details
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"  # Actual username for Neo4j
NEO4J_PASSWORD = "neo4j12345"  # Actual password for Neo4j

# Initialize the Neo4j connection
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Streamlit page configuration
st.set_page_config(page_title="Cyclone-G Visualization", layout="wide")

# Title of the Streamlit app
st.title("Cyclone-G Web Scraper Visualization")

# User input to enter the URL to be scraped
url_input = st.text_input("Enter the URL to scrape", "")

# Button to initiate the scraping process
if st.button("Scrape URL"):
    if url_input:
        # Call the backend scraper function with the provided URL
        scrape_url(url_input)
        st.success(f"Scraping completed for URL: {url_input}")
        # Retrieve data from Neo4j and visualize
        data = get_data_from_neo4j(url_input)
        visualize_data(data)
    else:
        st.error("Please enter a URL to scrape.")

# Function to retrieve data from Neo4j and visualize
def get_data_from_neo4j(url):
    with driver.session() as session:
        # Cypher query to retrieve nodes and relationships
        result = session.run("MATCH (n)-[r]->(m) WHERE n.url = $url RETURN n, r, m", url=url)
        # Process the result and prepare for visualization
        nodes = []
        edges = []
        for record in result:
            nodes.append(record['n'])
            edges.append({'source': record['n']['url'], 'target': record['m']['url']})
        return nodes, edges

# Function to visualize the data using Streamlit components
def visualize_data(data):
    nodes, edges = data
    # Use pyvis for graph visualization
    from pyvis.network import Network
    net = Network(height='100%', width='100%', bgcolor='#222222', font_color='white')

    # Add nodes and edges to the network
    for node in nodes:
        net.add_node(node['id'], label=node['title'], title=node['url'])
    for edge in edges:
        net.add_edge(edge['source'], edge['target'])

    # Generate and display the network
    net.show('graph.html')
    HtmlFile = open('graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=600)

# Additional Streamlit components as needed for the app functionality
# TODO: Add components for displaying additional information, settings, etc.
