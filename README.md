# Find Your Bias: A Microservices-Based Voting Analysis Application

This project is a fully containerized, cloud-native application that allows users to vote on various topics (tweets) and receive an AI-powered analysis of the overall political bias of the voting audience. It is built using a microservices architecture, with different components written in Python, .NET, and Node.js, all orchestrated by Kubernetes.

## How It Works

The application follows a decoupled, event-driven data flow:

1.  **Vote**: A Python Flask web server presents users with a random tweet and two voting options ("Agree" or "Disagree").
2.  **Queue**: When a user votes, the vote is not sent directly to the database. Instead, it is pushed as a message into a Redis list, which acts as a fast, in-memory message queue.
3.  **Worker**: A .NET worker service continuously monitors the Redis queue. As soon as a vote appears, the worker pops it from the queue and saves it to a persistent PostgreSQL database, adding a timestamp.
4.  **Result**: A Node.js Express application queries the database for all recent votes. It pushes this data in real-time to a web dashboard using Socket.IO, creating a live view of the current voting session.
5.  **AI Analysis**: From the results page, the user can click a button to request an analysis. This calls a dedicated Python Flask microservice (`ai-analyzer`). This service fetches the recent votes from the database, formats them into a prompt, and sends it to the AWS Bedrock API (Anthropic Claude model) to get a generative AI analysis of the audience's bias.

## Architecture & Technologies

The application is composed of five primary microservices and two data stores, all running in separate containers:

| Service       | Language / Framework | Purpose                                                                                             |
|---------------|----------------------|-----------------------------------------------------------------------------------------------------|
| **vote**      | Python, Flask        | Serves the voting web page and pushes votes to Redis.                                               |
| **worker**    | .NET                 | Processes votes from the Redis queue and persists them to the PostgreSQL database.                  |
| **result**    | Node.js, Express     | Serves the real-time results dashboard, communicating with clients via Socket.IO.                   |
| **ai-analyzer**| Python, Flask        | Exposes an API endpoint to perform AI analysis on the voting data using AWS Bedrock.                |
| **db**        | PostgreSQL           | The primary data store. Persistently stores all voting data. Deployed as a Kubernetes StatefulSet. |
| **redis**     | Redis                | An in-memory message queue that decouples the `vote` and `worker` services for scalability.         |

**Orchestration & Deployment:**
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions

## Project Progress
- [x] Add Progress bar1
- [x] Vote Microservice Deployment
- [x] Result Microservice Deployment
- [x] Worker Service Setup
- [x] Final Deployment 

test8

hpa done