# Multi-threaded API Web Server with Distributed Database

This project combines the implementation of a multi-threaded API web server with a distributed database using a Two-Phase Commit (2PC) protocol. It demonstrates dynamic content serving, user interactions, and data consistency across distributed systems in a seamless and cohesive manner.

## Features

### Web Server and Single Page Application (SPA)
- **Dynamic Content Serving**: A single-page application (SPA) served by a multi-threaded web server.
- **API Endpoints**:
  - `GET /api/tweet`: Retrieve all tweets.
  - `POST /api/tweet`: Create a new tweet (JSON payload).
  - `PUT /api/tweet/[tweet-id]`: Update a tweet by ID.
  - `POST /api/login`: Log in to the system (sets cookies for session tracking).
  - `DELETE /api/tweet/[tweet-id]`: Delete a tweet by ID.
  - `DELETE /api/login`: Log out of the system.
- **Cookie-based Access Control**: Only logged-in users can view or manipulate tweets.
- **Real-time Updates**: SPA uses JavaScript's `XMLHttpRequest` for all interactions without page refreshes.
- **Error Handling**: Provides appropriate responses for invalid paths or API calls.

### Distributed Database with Strong Consistency
- **Two-Phase Commit (2PC) Protocol**:
  - Worker nodes handle data storage and locking, while the server coordinates operations.
  - Ensures atomicity and consistency of operations across distributed nodes.
- **Concurrency Management**:
  - Supports multiple simultaneous requests.
  - Locks data items during updates to prevent conflicts.
- **Data Persistence**: Optional in-memory storage with preloaded data for testing.

### Unified Features
- **Integrated Frontend and Backend**: The SPA interacts with the distributed database through API calls for all actions.
- **Real-time User Feedback**: User actions (e.g., tweet creation, updates, and deletion) are reflected in the UI immediately.
- **Scalable Architecture**: The system supports multiple concurrent users and operations.

## Technology Stack
- **Backend**: Custom multi-threaded server implemented using socket programming.
- **Frontend**: JavaScript-based SPA utilizing `XMLHttpRequest` for asynchronous operations.
- **Distributed Database**: In-memory implementation with 2PC protocol.

## Setup and Running the Project

### Prerequisites
- Python 3.x
- Libraries: `socket`, `select`, `threading`, `argparse`, `uuid`, `json`

### How to Run

#### Design:
  - Client → Server/Coordinator → Worker(s)

#### Details:
- `webServer.py` assumes there are two workers whose addresses are stored in the variable `worker_addresses` as an array of tuples:
  ```python
  worker_addresses = [('localhost', 8355), ('localhost', 8359)]
  ```

#### To run the workers:
1. Workers get their port number from `sys.argv[1]`.
2. Run the workers:
   ```bash
   python3 worker.py 8355
   python3 worker.py 8359
   ```
3. If other ports are used, update the `worker_addresses` variable in `webServer.py`.
4. Each worker has two pre-defined tweets.

#### To run the web server:
- Execute:
  ```bash
  python3 server.py {PortNumber}
  ```

#### Load Testing:
- A script `load_test.py` makes 30 requests to create new tweets and fetch all tweets.
- To run the test:
  ```bash
  python3 load_test.py
  ```
- The hostname and port number for the server are stored in the script:
  ```python
  server_host = 'goose.cs.umanitoba.ca'
  server_port = 8357
  ```

## Testing
- **API**: Use tools like `curl` or Postman to interact with the API endpoints.
- **Frontend**: Open the SPA in a browser and log in as a user to test tweet creation, updates, and deletion.

## Challenges and Learning Outcomes
- Implementing concurrency and multi-threading for scalability.
- Designing and managing a distributed database with strong consistency guarantees.
- Developing a responsive SPA with real-time updates.
- Ensuring robust error handling and user-friendly feedback.

## Potential Improvements
- Implement persistent storage for the database.
- Add user authentication and session management.
- Optimize performance for large-scale deployments.

## Contact
Feel free to reach out for any questions or discussions related to the project.

---

This project was developed as part of a coursework assignment to demonstrate skills in network programming, distributed systems, and web development.