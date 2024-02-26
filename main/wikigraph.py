import uuid
from collections import deque

import bs4
import requests
from neo4j import GraphDatabase


def header_level(header):
    if header.lower().startswith('h') and len(header) == 2:
        try:
            return int(header[1])
        except ValueError:
            return "Error: Header must be in the format 'h1', 'h2', etc."
    else:
        return 10


class HTMLNode:
    def __init__(self, tag, text="", parent=None):
        self.id = str(uuid.uuid4())  # Generate a unique ID for each node
        self.tag = tag
        self.text = text
        self.children = []
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)

    def __str__(self, level=0):
        ret = "\t" * level + f"{self.tag.upper()}: {self.text.strip()}..." + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

    def level(self):
        return header_level(self.tag)

    def get_upper_node(self, level):
        if self.parent is None:
            return None
        if self.parent.level() < level:
            return self.parent
        else:
            return self.parent.get_upper_node(level)


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(user, password))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def create_html_node(self, node_id, tag, text):
        with self.__driver.session() as session:
            session.write_transaction(self._create_and_return_html_node, node_id, tag, text)

    @staticmethod
    def _create_and_return_html_node(tx, node_id, tag, text):
        query = (
            "CREATE (n:HTMLNode {id: $id, tag: $tag, text: $text}) "
            "RETURN n"
        )
        result = tx.run(query, id=node_id, tag=tag, text=text)
        try:
            return [{"tag": record["n"]["tag"], "text": record["n"]["text"]}
                    for record in result]
        except Exception as e:
            print("Query failed:", e)
            return None

    def create_relationship(self, parent_id, child_id):
        with self.__driver.session() as session:
            session.write_transaction(self._create_and_return_relationship, parent_id, child_id)

    @staticmethod
    def _create_and_return_relationship(tx, parent_id, child_id):
        query = (
            "MATCH (parent:HTMLNode {id: $parent_id}), "
            "(child:HTMLNode {id: $child_id}) "
            "CREATE (parent)-[:HAS_CHILD]->(child)"
        )
        result = tx.run(query, parent_id=parent_id, child_id=child_id)
        return result.single()


def traverse_and_create(node, neo4j_conn, parent=None):
    neo4j_conn.create_html_node(node.id, node.tag, node.text)
    if parent:
        neo4j_conn.create_relationship(parent.id, node.id)
    for child in node.children:
        traverse_and_create(child, neo4j_conn, parent=node)


def build_tree(html):
    soup = bs4.BeautifulSoup(html, features="html.parser")

    title = soup.find("span", class_="mw-page-title-main").text.strip()
    root = HTMLNode("h1", title)
    parent_node = root
    previous_node = root

    content = soup.find(class_="mw-content-ltr mw-parser-output")
    # content = soup.find(class_="excerpt")
    elements_queue = deque(content.find_all(recursive=False))  # Initialize queue with first-level elements

    while elements_queue:
        element = elements_queue.popleft()  # Get the first element from the queue

        # Processing exceptional case of processing excerpt block
        if element.name == "div" and "excerpt-block" in element.get('class', []):
            sub_elements = element.find_all("p",
                                            recursive=True)  # Assuming you meant to get sub_elements of the current element
            for sub_element in reversed(sub_elements):  # Add elements to the start of the deque
                elements_queue.appendleft(sub_element)
            continue  # Optionally skip further processing for this div, or remove 'continue' to process it as well

        if element.name not in ["h1", "h2", "h3", "p", "ul"]:
            continue
        if element.get("id") == "ioc" or element.get("role") == "navigation":
            continue  # Skip navigation sections

        new_level = header_level(element.name)
        if new_level > previous_node.level():
            parent_node = previous_node  # Move down in the hierarchy for headings
        elif new_level < previous_node.level():
            parent_node = previous_node.get_upper_node(new_level)

        if element.name == "ul":
            ul_text = element.get_text(separator=" ", strip=True)
            # Check if the last node was a 'p' and append, else create a new 'p' node
            if previous_node.tag == "p":
                previous_node.text += " " + ul_text  # Append ul text to the existing p node's text
            else:
                new_node = HTMLNode("p", ul_text, parent=parent_node)  # Create a new p node with ul text
                parent_node.add_child(new_node)
                previous_node = new_node
        else:
            if element.text.startswith("References"):
                return root

            new_node = HTMLNode(element.name, element.get_text(separator=" ", strip=True), parent=parent_node)
            parent_node.add_child(new_node)
            previous_node = new_node
    return root


def extract_from_wiki(url, html):
    tree = build_tree(html)
    print(f"Extraction from {url}")
    print(tree)
    return tree


if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/COVID-19'
    html = requests.get(url).text
    root = extract_from_wiki(url, html)

    # Connect to Neo4j
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    neo4j_conn = Neo4jConnection(uri, user, password)

    # Traverse and create
    traverse_and_create(root, neo4j_conn)

    # Close connection
    neo4j_conn.close()




    # from langchain_community.graphs import Neo4jGraph
    #
    # graph = Neo4jGraph(
    #     url="bolt://localhost:7687",
    #     username="neo4j",
    #     password="password"
    # )
    #
    # result = graph.query("""
    # MATCH (n)
    # RETURN n
    # LIMIT 5
    # """)
    #
    # print("Result")
    # print(result)
    # print("Graph schema")
    # print(graph.schema)
