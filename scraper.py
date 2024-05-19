from playwright.sync_api import sync_playwright
from scrapegraphai.graphs import OmniScraperGraph
from neo4j import GraphDatabase
import os

# Securely retrieved secrets for database connection and API key
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"  # Actual username for Neo4j
NEO4J_PASSWORD = "neo4j12345"  # Actual password for Neo4j
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Securely retrieved API key for OpenAI

# Debugging: Print the OPENAI_API_KEY to ensure it's being retrieved correctly
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")

def scrape_url(url):
    # Debugging: Confirming that the scrape_url function is being called
    print(f"Starting scrape_url function for URL: {url}")

    with sync_playwright() as p:
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the URL
        page.goto(url)

        # Extract the content of the page
        content = page.content()

        # Analyze the content with Scrapegraph-ai
        analyzed_data = analyze_content_with_scrapegraph_ai(content)

        # Save data to Neo4j
        save_data_to_neo4j(analyzed_data)

        # Close the browser
        browser.close()

def analyze_content_with_scrapegraph_ai(content):
    # Initialize OmniScraperGraph with necessary models and API keys
    graph_config = {
        "llm": {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "format": "json",
            "api_key": OPENAI_API_KEY
        },
        "embeddings": {
            "model": "models/embedding-001",  # Updated to a supported embeddings model
            "api_key": OPENAI_API_KEY
        },
        "verbose": True,
        "headless": True,
        "max_images": 5
    }

    omni_scraper_graph = OmniScraperGraph(
        prompt="List me all the projects with their descriptions",
        source="https://perinim.github.io/projects",
        config=graph_config
    )

    result = omni_scraper_graph.run()
    return result

def save_data_to_neo4j(data):
    # Function to save data to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        for page in data['pages']:
            session.write_transaction(create_page_node, page)

        for document in data['documents']:
            session.write_transaction(create_document_node, document)

        for link in data['links']:
            session.write_transaction(create_link_relationship, link['from'], link['to'])

    driver.close()

def create_page_node(tx, page):
    query = (
        "MERGE (p:Page {url: $url}) "
        "ON CREATE SET p.title = $title, p.timestamp = timestamp() "
        "RETURN p"
    )
    parameters = {"url": page['url'], "title": page['title']}
    return tx.run(query, parameters)

def create_document_node(tx, document):
    query = (
        "MERGE (d:Document {url: $url}) "
        "ON CREATE SET d.title = $title, d.timestamp = timestamp() "
        "RETURN d"
    )
    parameters = {"url": document['url'], "title": document['title']}
    return tx.run(query, parameters)

def create_link_relationship(tx, from_url, to_url):
    query = (
        "MATCH (p1:Page {url: $from_url}), (p2:Page {url: $to_url}) "
        "MERGE (p1)-[:LINKS_TO]->(p2)"
    )
    parameters = {"from_url": from_url, "to_url": to_url}
    return tx.run(query, parameters)

# Placeholder URL for testing
test_url = 'http://example.com'
scrape_url(test_url)
