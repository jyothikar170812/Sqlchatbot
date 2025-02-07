from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware


groq_api_key = 'API_KEY'
os.environ["TAVILY_API_KEY"] = 'TAVILY_API_KEY'

tool_tavily = TavilySearchResults(max_results=1)  
tools = [tool_tavily, ]
MODEL_NAMES = ["llama3-70b-8192", "mixtral-8x7b-32768"]


app = FastAPI(title='LangGraph AI SQL Agent')


DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def execute_query(query):
    """Executes an SQL query and returns results."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return {"error": str(e)}

# SQL Query Prompt
SQL_PROMPT_TEMPLATE = """
You are an SQL query generator for a PostgreSQL database. Based on the user's request, generate a valid SQL query.

### **Database Schema:**
**Products Table**
- ID (INTEGER, Primary Key)
- name (TEXT)
- brand (TEXT)
- price (DECIMAL)
- category (TEXT)
- description (TEXT)
- supplier_id (INTEGER, Foreign Key → Suppliers.ID)

**Suppliers Table**
- ID (INTEGER, Primary Key)
- name (TEXT)
- contact_info (TEXT)
- product_categories (TEXT ARRAY)

### **Rules:**
1. Generate valid **PostgreSQL** queries.
2. Use **JOINs** where necessary.
3. Optimize filtering using **WHERE, LIKE, and ILIKE**.
4. Use **ORDER BY and LIMIT** when applicable.
5. Return only query as response
6. Return without escape quotes

**User Query:** "{user_query}"

**Response should be only query** 
### **Examples:**
#### **User Query: "Show me all products under brand Apple."**
```sql
SELECT * FROM Products WHERE brand = 'Apple';

User Query: "Which suppliers provide laptops?"
```sql
SELECT * FROM Suppliers WHERE 'Laptops' = ANY(product_categories);

"""

origins = [
    "http://localhost:3000",  # React frontend (Dev)
    "http://127.0.0.1:3000",   # React frontend (Alternate)
    "https://your-frontend.com",  # Production frontend
    "*",  # Allow all origins (Not recommended for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Request Model
class RequestState(BaseModel):
    model_name: str
    user_query: List[str]
    system_prompt: str

# API Endpoint
@app.post("/chat")
def chat_endpoint(request: RequestState):
    """Processes user input and returns chatbot response."""
    if request.model_name not in MODEL_NAMES:
        return {"error": "Invalid model name. Please select a valid model."}

    llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)

    # Generate SQL Query using LLM
    prompt = SQL_PROMPT_TEMPLATE.format(user_query=request.user_query)
    # sql_query = llm.invoke(prompt)

    # agent = create_react_agent(llm, tools=tools, state_modifier=request.system_prompt)

    # # Create the initial state for processing
    # state = {"messages": prompt}

    # # Process the state using the agent
    # sql_query = agent.invoke(state)
    result= llm.invoke(prompt)
    resp = dict(result);
    print(resp['content'])
    sql_query=resp['content']
    if "error" in sql_query.lower():
        return {"error": "Could not generate SQL query from input."}

    # Execute SQL Query
    db_results = execute_query(sql_query)

    return {"query": sql_query, "results": db_results}

# Run FastAPI Server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
