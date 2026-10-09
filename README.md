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
