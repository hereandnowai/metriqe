from mcp.server.fastmcp import FastMCP
import uvicorn                            

#create a server
server = FastMCP("My calculator Server")

#Declare and Create the Tool
@server.tool(name="evaluate_expression", description= "Evaluates a mathematical expression and returns a result")
def evaluate_expression(expression: str)->float:
    """Evaluates a mathematical expression and returns a result"""
    try:
        result = eval(expression,{"__builtin__":{}},{"sum":sum})
        return result
    except Exception as e:
        raise ValueError(f"Invalid Expression : {e} ")

app = server.sse_app()

if __name__ == "__main__":
    print("MCP Server started")
    uvicorn.run(app, host ="127.0.0.1" , port= 8000)

    