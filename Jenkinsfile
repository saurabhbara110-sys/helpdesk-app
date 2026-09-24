pipeline {
    agent any
    environment {
        IMAGE_NAME = 'helpdesk-app'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('SonarQube Scan') {
           steps {
             script {
                def scannerHome = tool 'sonar-scanner'
                withSonarQubeEnv('sonarqube-helpdesk') {
                  sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=helpdesk-app -Dsonar.sources=."

                    }
                 }
              }
           }
        stage('Quality Gate') {
             steps {
                 timeout(time: 5, unit: 'Minutes') {
                waitForQualityGate abortPipeline: true
                 }
              }
           }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }
        stage('Deploy Multi-container') {
            steps {
                withCredentials ( [usernamePassword(
                credentialsId: 'helpdesk-db-credentials',
                usernameVariable: 'DB_USER',
                passwordVariable: 'DB_PASSWORD'
             )]) {
                sh 'docker compose up -d'
            }
         }
      }
   }
}
