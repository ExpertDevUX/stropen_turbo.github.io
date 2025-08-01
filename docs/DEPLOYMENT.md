# Advanced Streaming Panel - Deployment Guide

Complete deployment guide for production environments, including cloud platforms, on-premises installations, and containerized deployments.

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Cloud Deployments](#cloud-deployments)
4. [Container Deployments](#container-deployments)
5. [Traditional Server Deployment](#traditional-server-deployment)
6. [Load Balancing & Scaling](#load-balancing--scaling)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Security Hardening](#security-hardening)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## Overview

The Advanced Streaming Panel can be deployed in various environments:

- **Cloud Platforms**: AWS, Google Cloud, Azure, DigitalOcean
- **Container Platforms**: Docker, Kubernetes, Docker Swarm
- **Traditional Servers**: Linux VPS, dedicated servers
- **Hybrid Deployments**: Multi-region, edge computing

### Architecture Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Servers   │    │   RTMP Servers  │
│    (Nginx/LB)   │    │  (Gunicorn+App) │    │  (Nginx-RTMP)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────────┐
         │                                                         │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Database     │    │      Redis      │    │   File Storage  │
│  (PostgreSQL)   │    │     (Cache)     │    │   (Media Files) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## System Requirements

### Minimum Requirements

| Component | Specification |
|-----------|--------------|
| CPU | 4 cores @ 2.5 GHz |
| RAM | 8 GB |
| Storage | 100 GB SSD |
| Network | 50 Mbps upload |
| OS | Ubuntu 20.04+ / CentOS 8+ |

### Recommended Requirements

| Component | Specification |
|-----------|--------------|
| CPU | 8 cores @ 3.0 GHz |
| RAM | 32 GB |
| Storage | 500 GB NVMe SSD |
| Network | 1 Gbps upload |
| OS | Ubuntu 22.04 LTS |

### Scaling Guidelines

| Concurrent Streams | CPU Cores | RAM | Storage | Bandwidth |
|-------------------|-----------|-----|---------|-----------|
| 1-10 | 4 | 8 GB | 100 GB | 50 Mbps |
| 10-50 | 8 | 16 GB | 200 GB | 200 Mbps |
| 50-100 | 16 | 32 GB | 500 GB | 500 Mbps |
| 100+ | 32+ | 64 GB+ | 1 TB+ | 1 Gbps+ |

## Cloud Deployments

### AWS Deployment

#### EC2 Instance Setup

1. **Launch EC2 Instance:**
   ```bash
   # Use AWS CLI to create instance
   aws ec2 run-instances \
     --image-id ami-0c02fb55956c7d316 \
     --instance-type c5.2xlarge \
     --key-name your-key-pair \
     --security-groups streaming-panel-sg \
     --user-data file://user-data.sh
   ```

2. **Security Group Configuration:**
   ```bash
   # Create security group
   aws ec2 create-security-group \
     --group-name streaming-panel-sg \
     --description "Streaming Panel Security Group"
   
   # Add rules
   aws ec2 authorize-security-group-ingress \
     --group-name streaming-panel-sg \
     --protocol tcp --port 80 --cidr 0.0.0.0/0
   
   aws ec2 authorize-security-group-ingress \
     --group-name streaming-panel-sg \
     --protocol tcp --port 443 --cidr 0.0.0.0/0
   
   aws ec2 authorize-security-group-ingress \
     --group-name streaming-panel-sg \
     --protocol tcp --port 1935 --cidr 0.0.0.0/0
   ```

3. **RDS Database Setup:**
   ```bash
   # Create RDS PostgreSQL instance
   aws rds create-db-instance \
     --db-instance-identifier streaming-panel-db \
     --db-instance-class db.t3.medium \
     --engine postgres \
     --engine-version 14.9 \
     --allocated-storage 100 \
     --storage-type gp2 \
     --db-name streamingpanel \
     --master-username dbadmin \
     --master-user-password your-secure-password \
     --vpc-security-group-ids sg-your-security-group
   ```

4. **ElastiCache Redis Setup:**
   ```bash
   # Create Redis cluster
   aws elasticache create-cache-cluster \
     --cache-cluster-id streaming-panel-redis \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   ```

5. **S3 Bucket for Media Storage:**
   ```bash
   # Create S3 bucket
   aws s3 mb s3://your-streaming-panel-media
   
   # Configure CORS
   aws s3api put-bucket-cors \
     --bucket your-streaming-panel-media \
     --cors-configuration file://cors.json
   ```

#### CloudFormation Template

Create `aws-infrastructure.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Advanced Streaming Panel Infrastructure'

Parameters:
  InstanceType:
    Type: String
    Default: c5.2xlarge
    Description: EC2 instance type
  
  DBInstanceClass:
    Type: String
    Default: db.t3.medium
    Description: RDS instance class

Resources:
  # VPC Configuration
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: StreamingPanel-VPC

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: StreamingPanel-IGW

  # Attach Gateway to VPC
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: StreamingPanel-PublicSubnet

  # Private Subnet for Database
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      Tags:
        - Key: Name
          Value: StreamingPanel-PrivateSubnet

  # Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: StreamingPanel-PublicRouteTable

  # Route to Internet
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  # Associate Route Table with Subnet
  PublicSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

  # Security Group for Web Server
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for streaming panel web server
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 1935
          ToPort: 1935
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

  # RDS Subnet Group
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS database
      SubnetIds:
        - !Ref PublicSubnet
        - !Ref PrivateSubnet
      Tags:
        - Key: Name
          Value: StreamingPanel-DBSubnetGroup

  # RDS Instance
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: streaming-panel-db
      DBInstanceClass: !Ref DBInstanceClass
      Engine: postgres
      EngineVersion: '14.9'
      AllocatedStorage: 100
      StorageType: gp2
      DBName: streamingpanel
      MasterUsername: dbadmin
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DatabaseSecret}:SecretString:password}}'
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      PreferredBackupWindow: 03:00-04:00
      PreferredMaintenanceWindow: sun:04:00-sun:05:00

  # Database Secret
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Description: Database credentials for streaming panel
      GenerateSecretString:
        SecretStringTemplate: '{"username": "dbadmin"}'
        GenerateStringKey: 'password'
        PasswordLength: 32
        ExcludeCharacters: '"@/\'

  # EC2 Instance
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316
      InstanceType: !Ref InstanceType
      KeyName: your-key-pair
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          curl -fsSL https://raw.githubusercontent.com/expertdevux/streaming-panel/main/install.sh | bash
          
  # S3 Bucket for Media Storage
  MediaBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'streaming-panel-media-${AWS::AccountId}'
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders: ['*']
            AllowedMethods: [GET, PUT, POST, DELETE]
            AllowedOrigins: ['*']
            MaxAge: 3600

Outputs:
  WebServerIP:
    Description: Public IP of the web server
    Value: !GetAtt WebServer.PublicIp
  
  DatabaseEndpoint:
    Description: RDS database endpoint
    Value: !GetAtt Database.Endpoint.Address
  
  MediaBucketName:
    Description: S3 bucket for media storage
    Value: !Ref MediaBucket
```

Deploy with:
```bash
aws cloudformation create-stack \
  --stack-name streaming-panel \
  --template-body file://aws-infrastructure.yaml \
  --parameters ParameterKey=InstanceType,ParameterValue=c5.2xlarge
```

### Google Cloud Platform Deployment

#### GCE Instance Setup

1. **Create Instance:**
   ```bash
   gcloud compute instances create streaming-panel \
     --zone=us-central1-a \
     --machine-type=c2-standard-8 \
     --subnet=default \
     --network-tier=PREMIUM \
     --metadata-from-file startup-script=startup.sh \
     --boot-disk-size=100GB \
     --boot-disk-type=pd-ssd \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud
   ```

2. **Cloud SQL Database:**
   ```bash
   gcloud sql instances create streaming-panel-db \
     --database-version=POSTGRES_14 \
     --tier=db-custom-2-7680 \
     --region=us-central1 \
     --storage-size=100GB \
     --storage-type=SSD
   ```

3. **Firewall Rules:**
   ```bash
   gcloud compute firewall-rules create allow-streaming-panel \
     --allow tcp:80,tcp:443,tcp:1935 \
     --source-ranges 0.0.0.0/0 \
     --description "Allow streaming panel traffic"
   ```

### Azure Deployment

#### ARM Template

Create `azure-template.json`:

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "vmSize": {
            "type": "string",
            "defaultValue": "Standard_D4s_v3",
            "metadata": {
                "description": "Size of the virtual machine"
            }
        }
    },
    "variables": {
        "vnetName": "streamingPanel-vnet",
        "subnetName": "default",
        "nsgName": "streamingPanel-nsg",
        "vmName": "streamingPanel-vm",
        "dbServerName": "[concat('streaming-panel-db-', uniqueString(resourceGroup().id))]"
    },
    "resources": [
        {
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2021-02-01",
            "name": "[variables('vnetName')]",
            "location": "[resourceGroup().location]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": ["10.0.0.0/16"]
                },
                "subnets": [
                    {
                        "name": "[variables('subnetName')]",
                        "properties": {
                            "addressPrefix": "10.0.0.0/24"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.DBforPostgreSQL/flexibleServers",
            "apiVersion": "2021-06-01",
            "name": "[variables('dbServerName')]",
            "location": "[resourceGroup().location]",
            "sku": {
                "name": "Standard_D2s_v3",
                "tier": "GeneralPurpose"
            },
            "properties": {
                "administratorLogin": "dbadmin",
                "administratorLoginPassword": "YourSecurePassword123!",
                "version": "14",
                "storage": {
                    "storageSizeGB": 128
                }
            }
        }
    ]
}
```

Deploy with:
```bash
az deployment group create \
  --resource-group streaming-panel-rg \
  --template-file azure-template.json
```

## Container Deployments

### Docker Deployment

#### Single Container

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nginx \
    supervisor \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy configuration files
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories
RUN mkdir -p /app/static/streams/hls \
    && mkdir -p /app/static/streams/dash \
    && mkdir -p /app/logs

# Set permissions
RUN chown -R www-data:www-data /app

# Expose ports
EXPOSE 80 1935

# Start services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "80:80"
      - "1935:1935"
    environment:
      - DATABASE_URL=postgresql://dbuser:dbpass@db:5432/streamingpanel
      - REDIS_URL=redis://redis:6379
      - SESSION_SECRET=your-secret-key
    volumes:
      - ./static/streams:/app/static/streams
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=streamingpanel
      - POSTGRES_USER=dbuser
      - POSTGRES_PASSWORD=dbpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./docker/nginx-proxy.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

Deploy with:
```bash
docker-compose up -d
```

### Kubernetes Deployment

#### Namespace and ConfigMap

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: streaming-panel
```

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: streaming-panel-config
  namespace: streaming-panel
data:
  REDIS_URL: "redis://redis-service:6379"
  FFMPEG_PATH: "/usr/bin/ffmpeg"
  HLS_PATH: "/app/static/streams/hls"
  DASH_PATH: "/app/static/streams/dash"
```

#### Secrets

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: streaming-panel-secrets
  namespace: streaming-panel
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL2RidXNlcjpkYnBhc3NAcG9zdGdyZXMtc2VydmljZTo1NDMyL3N0cmVhbWluZ3BhbmVs
  SESSION_SECRET: eW91ci1zZWNyZXQta2V5LWhlcmU=
```

#### Application Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: streaming-panel
  namespace: streaming-panel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: streaming-panel
  template:
    metadata:
      labels:
        app: streaming-panel
    spec:
      containers:
      - name: streaming-panel
        image: expertdevux/streaming-panel:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: streaming-panel-secrets
              key: DATABASE_URL
        - name: SESSION_SECRET
          valueFrom:
            secretKeyRef:
              name: streaming-panel-secrets
              key: SESSION_SECRET
        envFrom:
        - configMapRef:
            name: streaming-panel-config
        volumeMounts:
        - name: media-storage
          mountPath: /app/static/streams
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
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
      volumes:
      - name: media-storage
        persistentVolumeClaim:
          claimName: media-storage-pvc
```

#### Services

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: streaming-panel-service
  namespace: streaming-panel
spec:
  selector:
    app: streaming-panel
  ports:
  - name: http
    port: 80
    targetPort: 5000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: rtmp-service
  namespace: streaming-panel
spec:
  selector:
    app: streaming-panel
  ports:
  - name: rtmp
    port: 1935
    targetPort: 1935
  type: LoadBalancer
```

#### Ingress

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: streaming-panel-ingress
  namespace: streaming-panel
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
spec:
  tls:
  - hosts:
    - streaming.yourdomain.com
    secretName: streaming-panel-tls
  rules:
  - host: streaming.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: streaming-panel-service
            port:
              number: 80
```

Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

### Helm Chart

Create `helm/Chart.yaml`:

```yaml
apiVersion: v2
name: streaming-panel
description: Advanced Streaming Panel Helm Chart
type: application
version: 1.0.0
appVersion: "2.1.0"
```

Create `helm/values.yaml`:

```yaml
replicaCount: 3

image:
  repository: expertdevux/streaming-panel
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: streaming.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: streaming-panel-tls
      hosts:
        - streaming.yourdomain.com

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

postgresql:
  enabled: true
  auth:
    username: streamuser
    password: securepassword
    database: streamingpanel

redis:
  enabled: true
  auth:
    enabled: false

persistence:
  enabled: true
  size: 100Gi
  storageClass: "standard"
```

Install with Helm:
```bash
helm install streaming-panel ./helm
```

## Traditional Server Deployment

### Ubuntu/Debian Server

1. **System Preparation:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install -y python3.11 python3.11-venv python3-pip
   sudo apt install -y postgresql nginx redis-server ffmpeg
   sudo apt install -y supervisor certbot python3-certbot-nginx
   ```

2. **Application Setup:**
   ```bash
   # Create application user
   sudo useradd -m -s /bin/bash streaming
   sudo usermod -aG www-data streaming
   
   # Create application directory
   sudo mkdir -p /opt/streaming-panel
   sudo chown streaming:streaming /opt/streaming-panel
   
   # Switch to application user
   sudo -u streaming bash
   cd /opt/streaming-panel
   
   # Clone repository
   git clone https://github.com/expertdevux/streaming-panel.git .
   
   # Setup virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   ```bash
   # Create database user
   sudo -u postgres createuser streaming --pwprompt
   sudo -u postgres createdb streamingpanel --owner=streaming
   
   # Initialize database
   cd /opt/streaming-panel
   source venv/bin/activate
   python manage.py db upgrade
   ```

4. **Nginx Configuration:**
   ```bash
   sudo tee /etc/nginx/sites-available/streaming-panel << 'EOF'
   server {
       listen 80;
       server_name your-domain.com;
       
       client_max_body_size 100M;
       
       location /static/ {
           alias /opt/streaming-panel/static/;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   EOF
   
   sudo ln -s /etc/nginx/sites-available/streaming-panel /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **Systemd Service:**
   ```bash
   sudo tee /etc/systemd/system/streaming-panel.service << 'EOF'
   [Unit]
   Description=Advanced Streaming Panel
   After=network.target postgresql.service redis.service
   Requires=postgresql.service redis.service
   
   [Service]
   Type=notify
   User=streaming
   Group=streaming
   WorkingDirectory=/opt/streaming-panel
   Environment=PATH=/opt/streaming-panel/venv/bin
   ExecStart=/opt/streaming-panel/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 main:app
   ExecReload=/bin/kill -s HUP $MAINPID
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   sudo systemctl daemon-reload
   sudo systemctl enable streaming-panel
   sudo systemctl start streaming-panel
   ```

### CentOS/RHEL Server

1. **Install EPEL and dependencies:**
   ```bash
   sudo yum install -y epel-release
   sudo yum update -y
   sudo yum install -y python3.11 python3-pip postgresql-server nginx redis
   sudo yum install -y ffmpeg supervisor certbot python3-certbot-nginx
   ```

2. **Initialize PostgreSQL:**
   ```bash
   sudo postgresql-setup --initdb
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   ```

3. **Follow similar steps as Ubuntu** for application setup and configuration.

## Load Balancing & Scaling

### Nginx Load Balancer

Create `nginx-lb.conf`:

```nginx
upstream streaming_backends {
    least_conn;
    server 10.0.1.10:5000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:5000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:5000 weight=2 max_fails=3 fail_timeout=30s;
}

upstream rtmp_backends {
    ip_hash;
    server 10.0.1.10:1935;
    server 10.0.1.11:1935;
    server 10.0.1.12:1935;
}

server {
    listen 80;
    listen 443 ssl http2;
    server_name streaming.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/streaming.yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/streaming.yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=streaming:10m rate=1r/s;
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://streaming_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /stream/ {
        limit_req zone=streaming burst=5 nodelay;
        proxy_pass http://streaming_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://streaming_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# RTMP Load Balancer
stream {
    upstream rtmp_backend {
        server 10.0.1.10:1935;
        server 10.0.1.11:1935;
        server 10.0.1.12:1935;
    }
    
    server {
        listen 1935;
        proxy_pass rtmp_backend;
        proxy_timeout 1s;
        proxy_responses 1;
    }
}
```

### HAProxy Configuration

Create `haproxy.cfg`:

```
global
    daemon
    maxconn 4096
    log stdout local0

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog

frontend streaming_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/streaming.pem
    redirect scheme https if !{ ssl_fc }
    
    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request reject if { sc_http_req_rate(0) gt 20 }
    
    default_backend streaming_backend

backend streaming_backend
    balance roundrobin
    option httpchk GET /health
    
    server app1 10.0.1.10:5000 check
    server app2 10.0.1.11:5000 check
    server app3 10.0.1.12:5000 check

frontend rtmp_frontend
    mode tcp
    bind *:1935
    default_backend rtmp_backend

backend rtmp_backend
    mode tcp
    balance source
    
    server rtmp1 10.0.1.10:1935 check
    server rtmp2 10.0.1.11:1935 check
    server rtmp3 10.0.1.12:1935 check

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
```

### Auto Scaling with Kubernetes HPA

Create `k8s/hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: streaming-panel-hpa
  namespace: streaming-panel
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: streaming-panel
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

## Monitoring & Maintenance

### Prometheus Monitoring

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'streaming-panel'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### Grafana Dashboard

Create dashboard JSON for streaming metrics:

```json
{
  "dashboard": {
    "title": "Streaming Panel Monitoring",
    "panels": [
      {
        "title": "Active Streams",
        "type": "stat",
        "targets": [
          {
            "expr": "streaming_panel_active_streams"
          }
        ]
      },
      {
        "title": "Concurrent Viewers",
        "type": "graph",
        "targets": [
          {
            "expr": "streaming_panel_viewers_total"
          }
        ]
      },
      {
        "title": "Bandwidth Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(streaming_panel_bytes_sent_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Health Check Endpoints

Add to your Flask application:

```python
@app.route('/health')
def health_check():
    """Basic health check endpoint"""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        # Check Redis connectivity
        redis_client.ping()
        
        # Check disk space
        disk_usage = shutil.disk_usage('/opt/streaming-panel')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent < 10:
            return jsonify({
                'status': 'warning',
                'message': 'Low disk space',
                'disk_free_percent': free_percent
            }), 200
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', '1.0.0')
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@app.route('/health/deep')
def deep_health_check():
    """Comprehensive health check"""
    checks = {}
    overall_status = 'healthy'
    
    # Database check
    try:
        result = db.session.execute('SELECT COUNT(*) FROM streams')
        checks['database'] = {
            'status': 'healthy',
            'stream_count': result.scalar()
        }
    except Exception as e:
        checks['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    # RTMP server check
    try:
        rtmp_status = get_rtmp_server_status()
        checks['rtmp_server'] = {
            'status': 'healthy' if rtmp_status['running'] else 'stopped',
            'active_streams': rtmp_status.get('active_streams', 0)
        }
    except Exception as e:
        checks['rtmp_server'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        if overall_status == 'healthy':
            overall_status = 'degraded'
    
    return jsonify({
        'status': overall_status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if overall_status != 'unhealthy' else 503
```

### Log Aggregation

#### ELK Stack Configuration

Create `docker-compose-elk.yml`:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml
      - /opt/streaming-panel/logs:/var/log/streaming-panel
    depends_on:
      - logstash

volumes:
  elasticsearch_data:
```

Create `logstash/pipeline/logstash.conf`:

```
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "streaming-panel" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "streaming-panel-%{+YYYY.MM.dd}"
  }
}
```

## Security Hardening

### Firewall Configuration

#### UFW (Ubuntu/Debian)

```bash
# Reset firewall
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH access
sudo ufw allow 22/tcp

# Web traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# RTMP traffic
sudo ufw allow 1935/tcp

# Monitoring (restrict to specific IPs)
sudo ufw allow from 10.0.0.0/8 to any port 9090  # Prometheus
sudo ufw allow from 10.0.0.0/8 to any port 3000  # Grafana

# Enable firewall
sudo ufw enable
```

#### iptables Rules

Create `/etc/iptables/rules.v4`:

```bash
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

# Allow loopback
-A INPUT -i lo -j ACCEPT

# Allow established connections
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# SSH
-A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m limit --limit 3/min --limit-burst 3 -j ACCEPT

# HTTP/HTTPS
-A INPUT -p tcp --dport 80 -j ACCEPT
-A INPUT -p tcp --dport 443 -j ACCEPT

# RTMP
-A INPUT -p tcp --dport 1935 -j ACCEPT

# Rate limiting for RTMP
-A INPUT -p tcp --dport 1935 -m recent --set --name rtmp_limit
-A INPUT -p tcp --dport 1935 -m recent --update --seconds 60 --hitcount 10 --name rtmp_limit -j DROP

# Drop invalid packets
-A INPUT -m conntrack --ctstate INVALID -j DROP

# Log dropped packets
-A INPUT -j LOG --log-prefix "iptables dropped: "

COMMIT
```

### SSL/TLS Configuration

#### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d streaming.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Strong SSL Configuration

Update nginx SSL settings:

```nginx
server {
    listen 443 ssl http2;
    server_name streaming.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/streaming.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/streaming.yourdomain.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Other security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/streaming.yourdomain.com/chain.pem;
    
    # Your location blocks here...
}
```

### Application Security

#### Environment Variables Security

```bash
# Secure .env file permissions
chmod 600 /opt/streaming-panel/.env
chown streaming:streaming /opt/streaming-panel/.env

# Use secrets management in production
# AWS Secrets Manager, Azure Key Vault, etc.
```

#### Database Security

```sql
-- Create read-only user for monitoring
CREATE USER monitoring WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE streamingpanel TO monitoring;
GRANT USAGE ON SCHEMA public TO monitoring;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring;

-- Restrict application user permissions
REVOKE ALL ON SCHEMA information_schema FROM streaming;
REVOKE ALL ON SCHEMA pg_catalog FROM streaming;
```

## Backup & Recovery

### Database Backups

#### Automated PostgreSQL Backups

Create `/opt/streaming-panel/scripts/backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/database"
DB_NAME="streamingpanel"
DB_USER="streaming"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/streamingpanel_$(date +%Y%m%d_%H%M%S).sql.gz"

# Create backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Database backup completed: $BACKUP_FILE"
    
    # Upload to S3 (optional)
    aws s3 cp $BACKUP_FILE s3://your-backup-bucket/database/
    
    # Remove old backups
    find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
else
    echo "Database backup failed!"
    exit 1
fi
```

Set up cron job:
```bash
sudo crontab -e
# Add: 0 2 * * * /opt/streaming-panel/scripts/backup-db.sh
```

### Media Files Backup

Create `/opt/streaming-panel/scripts/backup-media.sh`:

```bash
#!/bin/bash

MEDIA_DIR="/opt/streaming-panel/static"
BACKUP_DIR="/opt/backups/media"
S3_BUCKET="your-backup-bucket"

# Sync to S3
aws s3 sync $MEDIA_DIR s3://$S3_BUCKET/media/ \
    --exclude "streams/*" \
    --delete

# Local backup (for recent files)
rsync -av --delete $MEDIA_DIR/ $BACKUP_DIR/
```

### Disaster Recovery Plan

Create `/opt/streaming-panel/docs/disaster-recovery.md`:

```markdown
# Disaster Recovery Procedures

## Recovery Time Objectives (RTO)
- Critical services: 1 hour
- Full functionality: 4 hours
- Historical data: 24 hours

## Recovery Point Objectives (RPO)
- Database: 1 hour (automated backups)
- Media files: 24 hours
- Configuration: Real-time (version control)

## Recovery Procedures

### 1. Server Failure
1. Launch new server from latest AMI/image
2. Restore application from Git repository
3. Restore database from latest backup
4. Update DNS records
5. Verify functionality

### 2. Database Corruption
1. Stop application services
2. Restore from latest backup
3. Apply transaction logs if available
4. Restart services
5. Verify data integrity

### 3. Complete Data Center Outage
1. Activate secondary region/data center
2. Update DNS to point to backup location
3. Restore services from backups
4. Monitor for issues
```

## Troubleshooting

### Common Issues

#### High CPU Usage

```bash
# Check processes
top -p $(pgrep -d, -f "streaming-panel|ffmpeg|nginx")

# Check FFmpeg processes
ps aux | grep ffmpeg

# Optimize encoding settings
# Reduce quality or use hardware acceleration
```

#### Memory Leaks

```bash
# Monitor memory usage
watch -n 1 'free -m && ps aux --sort=-%mem | head -10'

# Check for memory leaks in application
valgrind --tool=memcheck --leak-check=full python app.py
```

#### Network Issues

```bash
# Check bandwidth usage
iftop -i eth0

# Monitor connections
netstat -an | grep :1935
ss -tuln | grep :1935

# Test RTMP connectivity
ffmpeg -re -i test.mp4 -c copy -f flv rtmp://localhost:1935/live/test
```

#### Storage Issues

```bash
# Check disk usage
df -h
du -sh /opt/streaming-panel/static/streams/*

# Clean old streams
find /opt/streaming-panel/static/streams -mtime +7 -delete

# Monitor inode usage
df -i
```

### Performance Tuning

#### Kernel Parameters

Add to `/etc/sysctl.conf`:

```bash
# Network optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr

# File descriptor limits
fs.file-max = 1000000

# Shared memory
kernel.shmmax = 17179869184
kernel.shmall = 4194304
```

#### Application Tuning

Update gunicorn configuration:

```python
# gunicorn_config.py
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5
preload_app = True
```

### Monitoring Scripts

Create `/opt/streaming-panel/scripts/monitor.sh`:

```bash
#!/bin/bash

LOG_FILE="/var/log/streaming-panel-monitor.log"

check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo "$(date): $service is running" >> $LOG_FILE
    else
        echo "$(date): $service is down, attempting restart" >> $LOG_FILE
        systemctl restart $service
        
        # Send alert
        curl -X POST https://api.slack.com/webhooks/YOUR/WEBHOOK \
            -d "{\"text\": \"Service $service restarted on $(hostname)\"}"
    fi
}

# Check critical services
check_service streaming-panel
check_service nginx
check_service postgresql
check_service redis-server

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "$(date): Disk usage is $DISK_USAGE%, cleaning up" >> $LOG_FILE
    # Clean old streams
    find /opt/streaming-panel/static/streams -mtime +3 -delete
fi
```

Set up monitoring cron:
```bash
# Run every 5 minutes
*/5 * * * * /opt/streaming-panel/scripts/monitor.sh
```

---

This deployment guide covers comprehensive production deployment scenarios. Choose the deployment method that best fits your infrastructure requirements and scale needs.

For additional support with deployment, contact Expert Dev UX professional services at: support@expertdevux.com

---

*Copyright © 2025 Expert Dev UX. All rights reserved.*