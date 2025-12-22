# Deployment Guide for QR Code Scanner MCP

This guide covers multiple deployment options for the QR Code Scanner MCP server.

## Local Development

### Prerequisites
- Python 3.8+
- pip or conda

### Quick Start

```bash
# Clone or navigate to project
cd qr_code_scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m src.server
```

## Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t qr-code-scanner:latest .

# Run the container
docker run -p 5000:5000 qr-code-scanner:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f qr-code-scanner

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS

#### Option 1: AWS Lambda (with Docker)

1. Create ECR repository:
```bash
aws ecr create-repository --repository-name qr-code-scanner
```

2. Build and push image:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag qr-code-scanner:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/qr-code-scanner:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/qr-code-scanner:latest
```

3. Create Lambda function:
- Use container image
- Set memory to 512MB (for image processing)
- Set timeout to 300 seconds
- Set environment variables as needed

#### Option 2: AWS App Runner

1. Push image to ECR (same as above)
2. Create App Runner service:
   - Select ECR image URI
   - Set port 5000
   - Configure auto-scaling (0.5 - 4 vCPU)

#### Option 3: Amazon EC2

1. Launch EC2 instance (t3.medium or larger)
2. SSH into instance
3. Install Docker:
```bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user
```

4. Pull and run:
```bash
docker pull <your-registry>/qr-code-scanner:latest
docker run -d -p 5000:5000 <your-registry>/qr-code-scanner:latest
```

### Google Cloud Platform

#### Option 1: Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/qr-code-scanner

# Deploy to Cloud Run
gcloud run deploy qr-code-scanner \
  --image gcr.io/PROJECT_ID/qr-code-scanner \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars PROCESSING_TIMEOUT=30,MAX_IMAGE_SIZE=50
```

#### Option 2: Compute Engine

Similar to AWS EC2 deployment

#### Option 3: App Engine (Flexible)

Create `app.yaml`:
```yaml
runtime: python
env: flex
entrypoint: python -m src.server

env_variables:
  PROCESSING_TIMEOUT: "30"
  MAX_IMAGE_SIZE: "50"

manual_scaling:
  instances: 2
```

Deploy:
```bash
gcloud app deploy
```

### Microsoft Azure

#### Option 1: Container Instances

```bash
# Create resource group
az group create --name qr-scanner-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group qr-scanner-rg \
  --name qrscannerregistry \
  --sku Basic

# Push image
az acr build --registry qrscannerregistry \
  --image qr-code-scanner:latest .

# Deploy container
az container create \
  --resource-group qr-scanner-rg \
  --name qr-code-scanner \
  --image qrscannerregistry.azurecr.io/qr-code-scanner:latest \
  --ports 5000 \
  --cpu 1 \
  --memory 1 \
  --registry-login-server qrscannerregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password>
```

#### Option 2: Azure App Service

1. Create App Service Plan
2. Create Web App
3. Enable Docker deployment
4. Configure continuous deployment from container registry

#### Option 3: Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create --resource-group qr-scanner-rg \
  --name qr-scanner-aks \
  --node-count 2 \
  --enable-managed-identity

# Get credentials
az aks get-credentials --resource-group qr-scanner-rg \
  --name qr-scanner-aks

# Deploy using Kubernetes manifest (see below)
kubectl apply -f k8s-deployment.yaml
```

### Heroku

1. Create `Procfile`:
```
web: python -m src.server
```

2. Deploy:
```bash
heroku login
heroku create qr-code-scanner
git push heroku main
```

## Kubernetes Deployment

Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qr-code-scanner
spec:
  replicas: 2
  selector:
    matchLabels:
      app: qr-code-scanner
  template:
    metadata:
      labels:
        app: qr-code-scanner
    spec:
      containers:
      - name: qr-code-scanner
        image: <your-registry>/qr-code-scanner:latest
        ports:
        - containerPort: 5000
        env:
        - name: PROCESSING_TIMEOUT
          value: "30"
        - name: MAX_IMAGE_SIZE
          value: "50"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: qr-code-scanner-service
spec:
  selector:
    app: qr-code-scanner
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

## Integration with LlamaIndex

Update your LlamaIndex agent configuration:

```python
from llama_index.agent import AgentRunner
from llama_index.tools import Tool

# Define the QR scanner tool
qr_tool = Tool(
    name="scan_qr_code",
    func=qr_scanner.scan_image_file,
    description="Scan and validate QR codes in label images",
)

# Create agent
agent = AgentRunner.from_llm(
    llm=llm,
    tools=[qr_tool]
)
```

## Monitoring & Logging

### Set Environment Variables

```bash
export DEBUG=true  # Enable debug logging
export LOG_LEVEL=INFO  # Set log level
export PROCESSING_TIMEOUT=30  # Max processing time
export MAX_IMAGE_SIZE=50  # Max image size in MB
```

### View Logs

```bash
# Docker
docker logs -f <container-id>

# Kubernetes
kubectl logs deployment/qr-code-scanner -f

# Cloud Run
gcloud run logs read qr-code-scanner --limit 50

# Azure
az container logs --resource-group qr-scanner-rg --name qr-code-scanner
```

## Performance Tuning

1. **Image Preprocessing**: Resize large images before scanning
2. **GPU Acceleration**: Use GPU-enabled instances for faster processing
3. **Caching**: Cache results for repeated scans
4. **Load Balancing**: Use load balancers for horizontal scaling

## Security Best Practices

1. **API Keys**: Use environment variables for sensitive data
2. **Image Validation**: Validate image formats and sizes
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **HTTPS**: Use HTTPS for all deployments
5. **Access Control**: Implement authentication/authorization

## Troubleshooting

### Container fails to start
- Check image layers: `docker history <image>`
- Verify dependencies: `pip install -r requirements.txt`
- Check logs: `docker logs <container>`

### High memory usage
- Reduce image processing resolution
- Implement image size limits
- Use smaller base images

### Slow response times
- Enable GPU acceleration
- Use caching mechanisms
- Optimize image preprocessing

## Support

For additional help, refer to the main README.md or open an issue.
