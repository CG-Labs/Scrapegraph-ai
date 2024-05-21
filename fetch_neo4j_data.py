from neo4j import GraphDatabase

# This script will fetch data from the Neo4j database and format it for the D3.js visualization.

class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

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

def fetch_data(uri, user, pwd, query, parameters=None, db=None):
    conn = Neo4jConnection(uri, user, pwd)
    try:
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
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    pwd = "neo4j12345"
    query = """
    MATCH (n)-[r]->(m)
    RETURN n.url AS nodeUrl, n.name AS nodeName, m.url AS targetUrl, m.name AS targetName, r.type AS relationshipType
    """
    data = fetch_data(uri, user, pwd, query)
    print(data)
