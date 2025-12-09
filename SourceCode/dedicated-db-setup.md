# Dedicated Database Server Setup Guide

This guide explains how to set up your dedicated server to run MongoDB and Elasticsearch using Docker.

## Prerequisites

1.  **Dedicated Server**: A computer on the same local network (connected to the same router).
2.  **Docker**: Docker and Docker Compose must be installed on this server.

## Step 1: Prepare Files on Dedicated Server

1.  Create a folder on your dedicated server (e.g., `~/my-db-server`).
2.  Copy the following files from your development machine to this new folder:
    *   `docker-compose.db.yml` (rename it to `docker-compose.yml` on the server for convenience)
    *   The entire `elasticsearch` folder (containing the `Dockerfile`).

   **Directory Structure on Dedicated Server:**
   ```
   ~/my-db-server/
   ├── docker-compose.yml  <-- (This is the docker-compose.db.yml you copied)
   └── elasticsearch/
       └── Dockerfile
   ```

## Step 2: Run the Databases

1.  Open a terminal on the dedicated server.
2.  Navigate to the folder:
    ```bash
    cd ~/my-db-server
    ```
3.  Start the services:
    ```bash
    docker-compose up -d --build
    ```

## Step 3: Find Server IP Address

You need the IP address of this server to connect from your development machine.

*   **Windows**: Open Command Prompt and run `ipconfig`. Look for "IPv4 Address".
*   **Mac/Linux**: Open Terminal and run `ifconfig` or `ip addr`.

Let's assume the IP is `192.168.0.100`.

## Step 4: Access Kibana (Optional)

You can now access the Kibana dashboard to manage your Elasticsearch cluster.

1.  Open a web browser on any computer in the network.
2.  Go to `http://192.168.0.100:5601` (replace IP with your server's IP).
3.  Login with:
    *   **Username**: `elastic`
    *   **Password**: `pass123`

## Step 5: Update Development Configuration

On your **development machine** (where you run the frontend/backend):

1.  Open `backend/backend.env`.
2.  Update the connection strings:
    ```env
    # Replace 192.168.0.100 with your actual server IP
    MONGODB_URL=mongodb://192.168.0.100:27017
    
    # Elasticsearch connection
    ELASTICSEARCH_URL=http://192.168.0.100:9200
    ELASTICSEARCH_USERNAME=elastic
    ELASTICSEARCH_PASSWORD=pass123
    ```
3.  Restart your development app:
    ```bash
    docker-compose up --build
    ```

## Troubleshooting

*   **Connection Refused**: Ensure the dedicated server's firewall allows traffic on ports `27017`, `9200`, and `5601`.
*   **Elasticsearch Error**: If Elasticsearch crashes, check memory settings. It is configured to use 1GB heap.
