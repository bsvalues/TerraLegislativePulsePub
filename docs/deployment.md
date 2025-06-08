# TerraLegislativePulse Deployment Guide

## Prerequisites

- Kubernetes cluster (v1.19+)
- Helm (v3.0+)
- kubectl
- Docker
- Access to container registry

## Infrastructure Setup

1. **Kubernetes Cluster**
   ```bash
   # Verify cluster access
   kubectl cluster-info
   
   # Create namespace
   kubectl create namespace terralegislativepulse
   ```

2. **Storage Class**
   ```bash
   # Create storage class for persistent volumes
   kubectl apply -f deployment/kubernetes/storage/storage-class.yaml
   ```

3. **Secrets**
   ```bash
   # Create secrets
   kubectl create secret generic terralegislativepulse-secrets \
     --from-literal=database-url='postgresql://user:pass@host:5432/db' \
     --from-literal=redis-url='redis://host:6379' \
     --from-literal=jwt-secret='your-secret-key' \
     -n terralegislativepulse
   ```

## Application Deployment

1. **Build and Push Docker Image**
   ```bash
   # Build image
   docker build -t terralegislativepulse:latest .
   
   # Push to registry
   docker push your-registry/terralegislativepulse:latest
   ```

2. **Deploy Application**
   ```bash
   # Apply Kubernetes manifests
   kubectl apply -f deployment/kubernetes/base/
   
   # Verify deployment
   kubectl get pods -n terralegislativepulse
   ```

## Monitoring Setup

1. **Install Prometheus Stack**
   ```bash
   # Add Prometheus Helm repo
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   
   # Install Prometheus
   helm install prometheus prometheus-community/kube-prometheus-stack \
     -f deployment/monitoring/prometheus-values.yaml \
     -n monitoring
   ```

2. **Configure Alerts**
   ```bash
   # Apply alert rules
   kubectl apply -f deployment/monitoring/alert-rules.yaml
   ```

## Logging Setup

1. **Install Elasticsearch**
   ```bash
   # Add Elastic Helm repo
   helm repo add elastic https://helm.elastic.co
   
   # Install Elasticsearch
   helm install elasticsearch elastic/elasticsearch \
     -f deployment/logging/elasticsearch-values.yaml \
     -n logging
   ```

2. **Install Fluentd**
   ```bash
   # Apply Fluentd configuration
   kubectl apply -f deployment/logging/fluentd-config.yaml
   ```

## Scaling

1. **Horizontal Pod Autoscaling**
   ```bash
   # Apply HPA configuration
   kubectl apply -f deployment/kubernetes/autoscaling/hpa.yaml
   ```

2. **Vertical Pod Autoscaling**
   ```bash
   # Apply VPA configuration
   kubectl apply -f deployment/kubernetes/autoscaling/vpa.yaml
   ```

## Backup and Recovery

1. **Database Backup**
   ```bash
   # Create backup cronjob
   kubectl apply -f deployment/kubernetes/backup/backup-cronjob.yaml
   ```

2. **Restore Procedure**
   ```bash
   # Restore from backup
   kubectl apply -f deployment/kubernetes/backup/restore-job.yaml
   ```

## Security

1. **Network Policies**
   ```bash
   # Apply network policies
   kubectl apply -f deployment/kubernetes/security/network-policies.yaml
   ```

2. **Pod Security Policies**
   ```bash
   # Apply pod security policies
   kubectl apply -f deployment/kubernetes/security/pod-security-policies.yaml
   ```

## Maintenance

1. **Update Application**
   ```bash
   # Update deployment
   kubectl set image deployment/terralegislativepulse \
     terralegislativepulse=your-registry/terralegislativepulse:new-version
   ```

2. **Rollback**
   ```bash
   # Rollback to previous version
   kubectl rollout undo deployment/terralegislativepulse
   ```

## Troubleshooting

1. **Check Pod Logs**
   ```bash
   # View pod logs
   kubectl logs -f deployment/terralegislativepulse -n terralegislativepulse
   ```

2. **Check Metrics**
   ```bash
   # Access Grafana
   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
   ```

3. **Check Logs**
   ```bash
   # Access Kibana
   kubectl port-forward svc/elasticsearch-kibana 5601:5601 -n logging
   ``` 