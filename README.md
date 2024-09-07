# Online Blackjack Game

## Application Suitability
* **Real-Time Communication**: The game requires real-time communication between the client and the server to get the latest results of the game.
* **Redundancy and Scalability**: The game should be able to handle a large number of users and should be able to scale horizontally and reduce downtime in case of server failure.
* **Separation of Logic and Data**: The game logic should be separated from the data storage to allow for easier scaling and maintenance.

## Service Boundaries
![Service Boundaries](./images/system_diagram.jpg)
* The **Game Lobby** service will be a cluster managed by a load balancer and will handle the game logic and communication with the clients.
* The **User Manager** service will be a separate cluster managed by a load balancer and will handle user authentication and authorization with additional data manipulation options.
* The **Exchange API** service is a remote service that will be used to get the latest exchange rates for the game and stocked in the **Exchange Cache**.

## Technology Stack
#### Communication:
* **Gateway**: Python
* **Service Discovery**: Python
* **Load Balancer**: Python

#### Services:
* **Game Lobby**: Kotlin
* **User Manager**: JavaScript

#### Databases:
* **User SQL Database**: PostgreSQL
* **Transfers Graph Database**: TypeDB
* **Log NoSQL Database**: MongoDB
* **Exchange Cache**: Python (custom cache)

## Data Management

## Deployment and Scaling
The services will be deployed using Docker.
The **Game Lobby** and **User Manager** services will be deployed with replicas to handle the load and reduce downtime in case of server failure.
The **Exchange Cache** will be deployed as a separate service to handle the exchange rate caching in order to reduce the load on the **Exchange API** service. Will have an expiration time of 1 hour and will only be populated if unexisting or expired data is requested.
