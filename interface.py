from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, target_nodes):
        with self._driver.session() as session:
            try:
                targets = {target_nodes} if isinstance(target_nodes, int) else set(target_nodes)
                queue = [(start_node, [{'name': start_node}])]
                visited = set([start_node])
                
                while queue:
                    current_node, path = queue.pop(0)
                    
                    if current_node in targets:
                        return [{'path': path}]
                    
                    query = """
                        MATCH (current:Location {name: $current_node})-[:TRIP]->(neighbor:Location)
                        WHERE NOT neighbor.name IN $visited
                        RETURN neighbor.name AS neighbor
                    """
                    result = session.run(query, {
                        "current_node": current_node,
                        "visited": list(visited)
                    })
                    
                    for record in result:
                        neighbor = record["neighbor"]
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [{'name': neighbor}]))
                
                return [{'path': []}]
                
            except Exception as e:
                print(f"Error in BFS: {str(e)}")
                return [{'path': []}]
    
    def pagerank(self, max_iterations, weight_property):
        with self._driver.session() as session:
            # Create graph projection
            session.run("""
                CALL gds.graph.project(
                    'pagerank_graph',
                    'Location',
                    {
                        TRIP: {
                            type: 'TRIP',
                            orientation: 'NATURAL',
                            properties: [$weight_prop]
                        }
                    },
                    {
                        nodeProperties: ['name']
                    }
                )
                """, {"weight_prop": weight_property})
            
            try:
                # Run PageRank 
                result = session.run("""
                    CALL gds.pageRank.stream('pagerank_graph', {
                        maxIterations: $iterations,
                        dampingFactor: 0.85,
                        relationshipWeightProperty: $weight_prop
                    })
                    YIELD nodeId, score
                    RETURN gds.util.asNode(nodeId).name AS name, score
                    ORDER BY score DESC
                    """, {
                        "iterations": max_iterations,
                        "weight_prop": weight_property
                    })
                node = [{'name': record['name'], 'score': record['score']} for record in result]
                return (node[0], node[-1])
                
            finally:
                session.run("CALL gds.graph.drop('pagerank_graph')")



    

