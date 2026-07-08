# Cloud Infrastructure Monitoring with Prometheus & Grafana

A portfolio-ready, fully-automated DevOps monitoring stack that provisions AWS infrastructure using Terraform and deploys a containerized monitoring system (Prometheus, Grafana, Alertmanager, node-exporter, and cAdvisor) to monitor a custom-instrumented Python Flask application.

---

## Architecture Overview

```mermaid
graph TD
    subgraph "Local Machine"
        TF[Terraform CLI]
        DC[Docker Compose]
    end

    subgraph "AWS Cloud (ap-south-1)"
        subgraph "VPC (10.0.0.0/16)"
            subgraph "Public Subnet (10.0.1.0/24)"
                EIP[Elastic IP] <--> EC2[EC2 Instance: Ubuntu 22.04]
            end
            
            SG[Security Group]
            IGW[Internet Gateway]
            RT[Route Table]
        end
    end

    subgraph "EC2 Containerized Stack (Docker Compose Network)"
        App[Flask Demo App:8000]
        NE[Node Exporter:9100]
        CAD[cAdvisor:8080]
        Prom[Prometheus:9090]
        AM[Alertmanager:9093]
        Graf[Grafana:3000]
        
        %% Scrape Connections
        Prom -->|Scrapes /metrics| App
        Prom -->|Scrapes /metrics| NE
        Prom -->|Scrapes /metrics| CAD
        Prom -->|Self Scrape| Prom
        
        %% Alert Connections
        Prom -->|Sends Alerts| AM
        
        %% Visualization
        Graf -->|Queries| Prom
    end

    %% Network flows
    TF -->|Provisions| VPC
    SG -->|Allows Ports 22, 3000, 9090, 8000| EC2
    IGW <--> RT <--> Public Subnet
    
    classDef aws fill:#FF9900,stroke:#333,stroke-width:1px,color:#fff;
    classDef monitor fill:#1F4E79,stroke:#333,stroke-width:1px,color:#fff;
    class VPC,PublicSubnet,EC2,EIP,SG,IGW,RT aws;
    class App,NE,CAD,Prom,AM,Graf monitor;
```

---

## Features

* **Infrastructure as Code**: Modular Terraform files with remote-friendly variables to spin up a VPC, public subnets, internet gateways, elastic IP, routing tables, and security groups.
* **Dynamic Key Generation**: Automatically generates a secure SSH key pair locally without external dependencies and stores it as a PEM file.
* **Auto-Provisioning**: Automated EC2 bootstrapping using `user_data` to install Docker Engine and standalone Docker Compose on startup.
* **Scraping Architecture**: Unified scraping of host system metrics (via `node_exporter`), container-level metrics (via `cAdvisor`), custom application metrics (via Flask `prometheus_client`), and Prometheus internal telemetry.
* **Auto-configured Dashboards**: Grafana is pre-provisioned with data sources and a custom dashboard JSON displaying panels for CPU, Memory, Disk Write I/O, Container resources, and application throughput/latency.
* **Robust Alerting**: Prometheus alerting rules for critical scenarios:
  * **InstanceDown**: Target unreachable for >1m.
  * **HostHighCpuLoad**: CPU load > 80% for >5m.
  * **HostHighMemory**: Memory usage > 85% for >5m.
* **Operational Routing**: Alertmanager configured to route warnings and critical alerts to email/webhook placeholder targets.

---

## Repository Directory Structure

```text
├── .gitignore          # Git exclusion patterns (state, vars, pem keys)
├── README.md           # This architecture & setup guide
├── RUNBOOK.md          # Deployment environments & alert response guides
├── /terraform
│   ├── main.tf         # Main AWS compute and network resources
│   ├── variables.tf    # Declared input variables
│   ├── outputs.tf      # Elastic IP & SSH command outputs
│   ├── providers.tf    # Providers mapping (aws, tls, local)
│   └── terraform.tfvars.example  # Configuration template
├── /monitoring
│   ├── docker-compose.yml   # Multi-container stack definition
│   ├── prometheus.yml       # Scrape configuration & rule mapping
│   ├── alert_rules.yml      # Alert definitions (CPU, Mem, Down)
│   ├── alertmanager.yml     # Routing & receiver configurations
│   └── /grafana
│       └── /provisioning
│           ├── /datasources
│           │   └── datasource.yml  # Pre-provisioned Prometheus datasource
│           ├── /dashboards
│           │   └── dashboard.yml   # Pre-provisioned Dashboard provider
│           └── /dashboards
│               └── monitoring_dashboard.json # Custom Grafana dashboard panels
└── /demo-app
    ├── app.py          # Flask application with custom metrics instrumented
    ├── requirements.txt# Python dependencies (flask, prometheus-client, gunicorn)
    └── Dockerfile      # Lightweight multi-stage Python runtime build
```

---

## Prerequisites

1. **AWS CLI** configured on your local machine with appropriate IAM permissions.
2. **Terraform CLI** (v1.3.0 or higher) installed locally.
3. **Docker Desktop** running locally for testing.

---

## Step-by-Step Deployment Instructions

### Step 1: Initialize and Run Locally (Docker Compose)
To verify the monitoring stack before provisioning AWS resources:

1. Navigate to the `/monitoring` directory:
   ```bash
   cd monitoring
   ```

2. Build and spin up all containers:
   ```bash
   docker compose up --build -d
   ```

3. Verify that the services are running:
   ```bash
   docker compose ps
   ```

4. Access local dashboards:
   * **Demo App**: [http://localhost:8000](http://localhost:8000) (Trigger `/slow` or `/error` to simulate traffic)
   * **Prometheus**: [http://localhost:9090](http://localhost:9090)
   * **Grafana**: [http://localhost:3000](http://localhost:3000) (Login with `admin` / `admin`)

---

### Step 2: Provision Cloud Infrastructure (Terraform)

1. Navigate to the `/terraform` directory:
   ```bash
   cd ../terraform
   ```

2. Copy the example variable file and adjust values:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Initialize the workspace:
   ```bash
   terraform init
   ```

4. Preview the execution plan:
   ```bash
   terraform plan
   ```

5. Apply the plan to build the resources:
   ```bash
   terraform apply -auto-approve
   ```

6. Secure the generated private key file:
   ```bash
   chmod 400 monitoring-key.pem   # Linux/macOS
   # On Windows, permissions are automatically set to 0600 by local_file
   ```

---

### Step 3: Deploy Stack to EC2 Instance

1. Retrieve the output `ssh_command` and use it to connect:
   ```bash
   ssh -i monitoring-key.pem ubuntu@<elastic_ip>
   ```

2. Once connected, confirm Docker and Docker Compose are installed:
   ```bash
   docker --version
   docker compose version
   ```

3. Clone this repository (or copy your `/monitoring` and `/demo-app` folders to the server):
   ```bash
   git clone <your_git_repo_url>
   cd <repo_directory>/monitoring
   ```

4. Spin up the production-ready monitoring stack:
   ```bash
   docker compose up --build -d
   ```

5. Open your web browser and access your services at:
   * **Grafana**: `http://<elastic_ip>:3000` (user/pass: `admin/admin`)
   * **Prometheus**: `http://<elastic_ip>:9090`
   * **Demo App**: `http://<elastic_ip>:8000`