from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.agent import call_agent

# Create FastAPI app instance
app=FastAPI()

## used Swagger Customization
# app = FastAPI(
#     title="Federal Register RAG Agent",
#     description="Query US Federal Register documents using a local LLM with tool-calling.",
#     version="1.0.0",
#     contact={
#         "name": "Raj Aryan",
#         "email": "theraaajj@example.com"
#     },
#     license_info={
#         "name": "MIT License"
#     }
# )


# Enable CORS to allow frontend/local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request schema using Pydantic
class ChatRequest(BaseModel):
    query: str  # The user input query to be processed by the agent

# Define response schema
class ChatResponse(BaseModel):
    response: str  # The LLM or tool-augmented agent's final response

# Define a health check endpoint
@app.get("/")
def root():
    return {"message": "RAG Agent API is running"}

# Define main chat endpoint that takes a query and returns the response
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print("Received query:", request.query)
    try:
        agent_output = call_agent(request.query)
        print("Agent output:", agent_output)
        return {"response": agent_output}
    except Exception as e:
        print("Error in call_agent:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

