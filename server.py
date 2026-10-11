import sqlite3
from mcp.server import MCPServer
DB = "analytics.db"
MAX_ROWS = 100 


mcp = MCPServer("sqlite-analytics")


def connect() -> sqlite3.Connection:
    """ This is just a readonly connection to my database"""
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.execute("PRAGMA query_only = TRUE;")
    return con

@mcp.tool()
def list_tables() -> list[str]:
    """ List all the tables in the database """
    con = connect()
    try:
        rows = con.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        return [row[0] for row in rows]
    finally:
        con.close()

@mcp.tool()
def describe_table(table: str) -> str:
    """ Describe the table """
    con = connect()
    try:
        columns = con.execute(f"PRAGMA table_info({table});").fetchall()
        if not columns:
            return f"Table '{table}' does not exist."
        description = f"Table '{table}' has the following columns:\n"
        for col in columns:
            description += f"- {col[1]} ({col[2]})\n"
        return description
    finally:
        con.close()

@mcp.tool()
def run_query(query: str) -> str:
    """ Run a read only query and return the results """
    con = connect()
    try:
        cursor = con.execute(query)
        header = [description[0] for description in cursor.description]
        rows = cursor.fetchmany(MAX_ROWS)
        lines = [", ".join(header)]
        for row in rows:
            lines.append(", ".join(str(item) for item in row))  
        return "\n".join(lines)
    finally:
        con.close()

@mcp.prompt(name="explain-schema", title="Explain the schema")
def explain_schema() -> str:
    """ explains the schema of the database in plain english """

    return (
        " Read the schema resource and explain the schema of the database in plain english. , what each table stores and how the tables are related to each other. "
    )

@mcp.prompt(name="daily-digest", title="Daily Digest")
def daily_digest() -> str:
    """ It generates a quick snapshot of the key numbers"""
    return (
        " Give me a quick snapshot of the key numbers in the database, such as total number of users, total number of orders, total revenue, and any other relevant metrics in the last 7 days and also the total revenue"
    )



if __name__ == "__main__":
    mcp.run(transport="stdio")