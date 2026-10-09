# HelpDesk Application — DevOps CI/CD Project

## 1. Project Overview

The HelpDesk Application is a web-based ticket management system developed using Flask and PostgreSQL. It enables customers to raise support tickets and allows support personnel to manage, take ownership of, and resolve tickets through a web interface.

The project demonstrates an end-to-end DevOps workflow designed to automate application testing, code quality analysis, container image creation, and Kubernetes deployment.

The application is integrated with a Jenkins CI/CD pipeline that uses GitHub for source code management, pytest for automated testing and code coverage, SonarQube for static code analysis and Quality Gate enforcement, Docker for containerization, Docker Hub for image storage, and Helm for Kubernetes application deployment.

The application is deployed on a two-node Kubernetes cluster created using kind (Kubernetes in Docker). NGINX Ingress handles HTTP traffic routing to the HelpDesk application. PostgreSQL runs as a separate Kubernetes Deployment and Service, independently of the application's Helm release.

A key objective of this project is to enforce a quality-controlled CI/CD process. The pipeline must pass the SonarQube Quality Gate before proceeding to Docker image publishing and application deployment. If the Quality Gate fails, the pipeline stops before these stages, preventing an unsuccessful quality assessment from progressing to deployment.

### Project Objectives

* Develop a functional ticket management application with separate customer and support workflows.
* Automate application testing and code coverage reporting using pytest.
* Integrate SonarQube static code analysis and Quality Gate enforcement into Jenkins.
* Build Docker images and publish them to Docker Hub only after the required quality checks pass.
* Deploy and manage application releases on Kubernetes using Helm.
* Maintain PostgreSQL as a separate Kubernetes Deployment and Service outside the application Helm release.
* Manage application configuration and sensitive credentials using environment variables, Jenkins Credentials, and Kubernetes Secrets.
* Demonstrate an end-to-end CI/CD workflow using practical DevOps tools and infrastructure.

## 2. Technology Stack

The HelpDesk project uses a combination of application development, automated testing, continuous integration and delivery, containerization, code quality analysis, and Kubernetes deployment technologies.

### 2.1 Application Development and Testing

| Technology | Purpose                                                                                                   |
| ---------- | --------------------------------------------------------------------------------------------------------- |
| Python     | Programming language used to develop the application.                                                     |
| Flask      | Lightweight web framework used to implement ticket management, authentication, and application endpoints. |
| PostgreSQL | Relational database used to store application users and support tickets.                                  |
| pytest     | Automates application tests to verify expected behavior and identify regressions.                         |
| pytest-cov | Measures and reports code coverage during automated testing.                                              |

### 2.2 Source Control and CI/CD

| Technology                | Purpose                                                                                                                     |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Git                       | Tracks source code changes and supports version control.                                                                    |
| GitHub                    | Hosts the application repository and maintains the project history.                                                         |
| Jenkins                   | Orchestrates the CI/CD pipeline, including testing, quality checks, container image publishing, and application deployment. |
| SonarQube Community Build | Performs static code analysis and evaluates the project against the configured Quality Gate.                                |

SonarQube runs in a Docker container on the EC2 environment. The Jenkins pipeline connects to the running SonarQube instance to submit analysis results and enforce the Quality Gate before Docker image publishing and deployment.

### 2.3 Containerization and Image Management

| Technology | Purpose                                                                                 |
| ---------- | --------------------------------------------------------------------------------------- |
| Docker     | Packages the Flask application and its runtime dependencies into a container image.     |
| Docker Hub | Stores versioned application images so they can be retrieved for Kubernetes deployment. |

### 2.4 Kubernetes and Application Deployment

| Technology                  | Purpose                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------- |
| Kubernetes                  | Orchestrates application containers and manages application workloads.                  |
| kind (Kubernetes in Docker) | Provides the two-node Kubernetes cluster used for the project.                          |
| Helm                        | Packages and manages releases of the HelpDesk application and its Kubernetes resources. |
| NGINX Ingress Controller    | Routes incoming HTTP requests to the HelpDesk Kubernetes Service.                       |

The application is deployed through a Helm chart. PostgreSQL is maintained as a separate Kubernetes Deployment and Service, outside the application's Helm release.

### 2.5 Infrastructure and Configuration Management

| Technology            | Purpose                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| AWS EC2               | Provides the project environment for Jenkins, SonarQube, Docker, and the kind Kubernetes cluster. |
| Jenkins Credentials   | Securely stores and supplies credentials and sensitive configuration required by pipeline steps.  |
| Kubernetes Secrets    | Stores sensitive Kubernetes configuration, including the database password.                       |
| Kubernetes ConfigMaps | Supplies non-sensitive configuration to Kubernetes workloads.                                     |

The project uses a single EC2 instance for the overall environment. The kind cluster runs its control-plane and worker nodes as containers on that environment.

### 2.6 Planned Technologies

The following technologies are potential future improvements and are not presented as implemented components of the current workflow:

* **Argo CD:** GitOps-based Kubernetes deployment and reconciliation.
* **Prometheus:** Metrics collection and monitoring.
* **Grafana:** Monitoring dashboards and visualization.
* **Additional security scanners:** Integration of tools for source code, dependency, container image, and application security testing, as appropriate for the project.
