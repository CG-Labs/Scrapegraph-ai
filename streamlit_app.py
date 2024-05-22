import streamlit as st
from neo4j import GraphDatabase
import sys
import json
from dotenv import load_dotenv  # Import the load_dotenv function from python-dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

# Retrieve the OPENAI_API_KEY from the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

sys.path.append('/home/ubuntu/Scrapegraph-ai')  # Ensure scraper.py is findable
from scraper import scrape_url  # Import the scrape_url function
from fetch_neo4j_data import fetch_data  # Import the fetch_data function

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

# Function to visualize the data using Streamlit components
def visualize_data(data):
    # Convert data to JSON format for JavaScript compatibility
    data_json = json.dumps(data)

    # Load the D3.js visualization script
    st.markdown("""
        <div id="graph"></div>
        <script src="https://d3js.org/d3.v6.min.js"></script>
        <script src="/static/gource_like_visualization.js"></script>
        <script>
            // Call the updateVisualization function with the data
            updateVisualization(%s);
        </script>
    """ % data_json, unsafe_allow_html=True)

# Button to initiate the scraping process
if st.button("Scrape URL"):
    if url_input:
        try:
            # Call the backend scraper function with the provided URL
            scrape_url(url_input)
            st.success(f"Scraping completed for URL: {url_input}")
            # Retrieve data from Neo4j and visualize
            data = fetch_data(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, """
                MATCH (n)-[r]->(m)
                RETURN n.url AS nodeUrl, n.name AS nodeName, m.url AS targetUrl, m.name AS targetName, r.type AS relationshipType
            """)
            visualize_data(data)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a URL to scrape.")

# Additional Streamlit components as needed for the app functionality
# TODO: Add components for displaying additional information, settings, etc.
