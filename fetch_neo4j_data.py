from neo4j import GraphDatabase

# This script will fetch data from the Neo4j database and format it for the D3.js visualization.

class Neo4jConnection:

    def __init__(self, driver):
        self.__driver = driver

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

def fetch_data(driver, scrape_result, db=None):
    conn = Neo4jConnection(driver)
    try:
        # Construct the query using the scrape_result
        query = """
        MATCH (n)-[r]->(m)
        WHERE n.url = $url
        RETURN n.url AS nodeUrl, n.name AS nodeName, m.url AS targetUrl, m.name AS targetName, r.type AS relationshipType
        """
        parameters = {'url': scrape_result['url']}
        results = conn.query(query, parameters, db)
        nodes = []
        links = []
        for record in results:
            # Use the 'url' property as the unique identifier for nodes
            nodes.append({'id': record['nodeUrl'], 'label': record['nodeName']})
            # Check if the record contains a relationship and another node
            if 'relationshipType' in record and 'targetUrl' in record:
                links.append({
                    'source': record['nodeUrl'],
                    'target': record['targetUrl'],
                    'value': record['relationshipType']
                })
        return {'nodes': nodes, 'links': links}
    finally:
        conn.close()

# Example usage:
if __name__ == "__main__":
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "neo4j12345"))
    scrape_result = {'url': 'https://example.com'}
    data = fetch_data(driver, scrape_result)
    print(data)
