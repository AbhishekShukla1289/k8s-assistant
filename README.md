
# Kubernetes Query AI Agent

## Introduction
This project implements an AI-powered assistant capable of answering queries about a Kubernetes cluster. It leverages OpenAI's GPT models to process and respond to user queries by dynamically fetching real-time Kubernetes context.

## Objective
Create an AI agent that interacts with a Kubernetes cluster to answer queries about its resources, including deployments, pods, services, and nodes.

### Environment Variables
- Your API key should be stored in an `.env` file as `OPENAI_API_KEY`.

### API Specifications
Your agent provides a POST endpoint for query submission:
- URL: `http://localhost:8000/query`
- Port: 8000
- Payload format:
  ```json
  {
      "query": "How many pods are in the default namespace?"
  }
  ```

### Scope of Queries
- Queries will require only read actions from your agent.
- Topics include deployments, pods, services, nodes, and other Kubernetes resources.
- The agent dynamically generates responses based on the current state of the Kubernetes cluster.

---

## Usage Instructions

### Installation
1. **Clone the Repository**
   ```bash
   git clone k8s-assistant
   cd k8s-assistant
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` File**
   Create a `.env` file in the project directory and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=your-openai-api-key
   ```

### Starting the FastAPI Server
Run the server using the following command:
```bash
python3 main.py
```

Expected Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 
```

### Testing the Agent
1. **Using Swagger UI:**
   Open your browser and go to [http://localhost:8000/docs](http://localhost:8000/docs) to test the `/query` endpoint interactively.

---

## Evaluation Criteria
- **Accuracy of Answers:** Responses should align with the current state of the Kubernetes cluster.
- **Code Quality:** Well-structured, modular, and maintainable code.
- **Documentation Clarity:** Comprehensive README and detailed explanations.

---

## Example Queries and Responses
1. **Query:**
   - Q: "Which pod is spawned by my-deployment?"
   - A: "Pods spawned by deployment 'my-deployment': my-deployment-74bdc9fb86-7klqn, my-deployment-74bdc9fb86-x7mzq."

2. **Query:**
   - Q: "What is the status of the pod named 'example-pod'?"
   - A: "Running."

3. **Query:**
   - Q: "How many nodes are there in the cluster?"
   - A: "3 nodes: node1, node2, node3."

---

## Logs
Logs are stored in `agent.log` to help debug issues. Example:
```
2024-12-26 10:00:00 - Received query: How many pods are running?
2024-12-26 10:00:01 - Answer: Pods in namespace 'default': pod1, pod2, pod3.
```
