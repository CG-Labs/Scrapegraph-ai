from playwright.async_api import async_playwright
from scrapegraphai.graphs import OmniScraperGraph
from neo4j import GraphDatabase
import os
import asyncio

# Securely retrieved secrets for database connection and API key
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"  # Actual username for Neo4j
NEO4J_PASSWORD = "neo4j12345"  # Actual password for Neo4j
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Securely retrieved API key for OpenAI
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  # Securely retrieved API key for GROQ

# Debugging: Print the OPENAI_API_KEY to ensure it's being retrieved correctly
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")

async def scrape_url(url):
    # Debugging: Confirming that the scrape_url function is being called
    print(f"Starting scrape_url function for URL: {url}")
    scrape_data = None

    async with async_playwright() as p:
        # Launch the browser in headless mode
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the URL
        await page.goto(url)

        # Extract the content of the page
        content = await page.content()
        # Debugging: Print the extracted content
        print(f"Extracted content: {content[:500]}...")  # Print the first 500 characters of the content

        # Analyze the content with Scrapegraph-ai
        try:
            analyzed_data = await analyze_content_with_scrapegraph_ai(content)
            # Debugging: Print the analyzed data
            print(f"Analyzed data: {analyzed_data}")
            # Save data to Neo4j
            save_success = await save_data_to_neo4j(analyzed_data)
            # Debugging: Print the result of the save operation
            print(f"Data save success: {save_success}")
            if save_success:
                scrape_data = analyzed_data
        except Exception as e:
            print(f"An error occurred: {e}")

        # Close the browser
        await browser.close()

    return scrape_data

async def analyze_content_with_scrapegraph_ai(content):
    # Initialize OmniScraperGraph with necessary models and API keys
    graph_config = {
        "llm": {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "format": "json",
            "api_key": OPENAI_API_KEY  # Assuming this is for OpenAI's GPT models
        },
        "embeddings": {
            "model": "models/embedding-001",  # Assuming this is for OpenAI's embeddings
            "api_key": OPENAI_API_KEY
        },
        "groq": {
            "model": "models/text-bison-001",  # Correct model name for Google's generative AI
            "api_key": GROQ_API_KEY  # API key for GROQ's langchain-google-genai package
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

    result = await omni_scraper_graph.run()
    return result

async def save_data_to_neo4j(data):
    # Function to save data to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    save_success = False

    with driver.session() as session:
        try:
            for page in data['pages']:
                session.write_transaction(create_page_node, page)

            for document in data['documents']:
                session.write_transaction(create_document_node, document)

            for link in data['links']:
                session.write_transaction(create_link_relationship, link['from'], link['to'])
            save_success = True
        except Exception as e:
            print(f"An error occurred while saving to Neo4j: {e}")

    driver.close()
    return save_success

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

if __name__ == "__main__":
    # Run the scrape_url function as an asynchronous task
    asyncio.run(scrape_url(test_url))
