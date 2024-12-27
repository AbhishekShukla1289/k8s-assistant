import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from kubernetes import client, config
import openai
from dotenv import load_dotenv

# Set up logging to keep track of requests and issues
logging.basicConfig(filename="agent.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Load kubeconfig
try:
    config.load_kube_config(os.path.expanduser("~/.kube/config"))
except Exception as e:
    logging.error(f"Error loading kubeconfig: {e}")
    raise Exception("Unable to load kubeconfig file.")

# Initialize FastAPI
app = FastAPI()

# Define the structure of incoming requests and outgoing responses
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str

# Function to gather Kubernetes data for context
def fetch_kubernetes_context() -> str:
    try:
        apps_v1 = client.AppsV1Api()
        v1 = client.CoreV1Api()
        namespace = "default"

        context = []

        # Fetch Deployments and Pods
        deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
        for deployment in deployments.items:
            deployment_name = deployment.metadata.name
            replicas = deployment.spec.replicas or 0
            ready_replicas = deployment.status.ready_replicas or 0
            context.append(f"Deployment '{deployment_name}' has {ready_replicas}/{replicas} replicas ready.")

            # Fetch associated pods
            pods = v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}")
            pod_names = [pod.metadata.name for pod in pods.items]
            context.append(f"Pods spawned by deployment '{deployment_name}': {', '.join(pod_names)}.")

        # Fetch Services
        services = v1.list_namespaced_service(namespace=namespace)
        for service in services.items:
            service_name = service.metadata.name
            ports = ", ".join(str(port.port) for port in service.spec.ports)
            context.append(f"Service '{service_name}' exposes ports: {ports}.")

        # Fetch Pods Details
        pods = v1.list_namespaced_pod(namespace=namespace)
        for pod in pods.items:
            pod_name = pod.metadata.name
            status = pod.status.phase
            context.append(f"Pod '{pod_name}' is in phase '{status}'.")
            # Fetch environment variables
            for container in pod.spec.containers:
                if container.env:
                    env_vars = ", ".join(f"{env.name}={env.value}" for env in container.env if env.value)
                    context.append(f"Environment variables for pod '{pod_name}': {env_vars}.")
                # Fetch readiness probe
                if container.readiness_probe and container.readiness_probe.http_get:
                    context.append(f"Readiness probe for pod '{pod_name}' is at path '{container.readiness_probe.http_get.path}'.")

        # Fetch Persistent Volume Claims
        pvcs = v1.list_namespaced_persistent_volume_claim(namespace=namespace)
        for pvc in pvcs.items:
            pvc_name = pvc.metadata.name
            context.append(f"Persistent Volume Claim '{pvc_name}' is bound to storage.")

        # Fetch Nodes
        nodes = v1.list_node()
        for node in nodes.items:
            node_name = node.metadata.name
            node_status = [condition.status for condition in node.status.conditions if condition.type == "Ready"]
            context.append(f"Node '{node_name}' is {'Ready' if 'True' in node_status else 'Not Ready'}.")

        # Combine all context
        return "\n".join(context)
    except Exception as e:
        logging.error(f"Error fetching Kubernetes data: {e}")
        return "Error fetching Kubernetes context."

# OpenAI Query Handler
def get_openai_response(user_query: str, context: str) -> str:
    try:
        messages = [
            {"role": "system", "content": "You are a Kubernetes assistant. Use the provided context to answer the query."},
            {"role": "system", "content": f"Kubernetes Context:\n{context}"},
            {"role": "user", "content": user_query}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if available
            messages=messages,
            max_tokens=200
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return f"Error processing query: {e}"

# FastAPI Endpoint
@app.post("/query", response_model=QueryResponse)
def query_k8s_agent(request: QueryRequest):
    logging.info(f"Received query: {request.query}")

    # Fetch Kubernetes context
    context = fetch_kubernetes_context()

    # Get OpenAI response
    answer = get_openai_response(request.query, context)

    logging.info(f"Answer: {answer}")
    return QueryResponse(query=request.query, answer=answer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
