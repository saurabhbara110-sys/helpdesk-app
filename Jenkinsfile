pipeline {
    agent any
    environment {
        DOCKERHUB_REPO = 'saurabhbara110/helpdesk-app'
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
                 timeout(time: 5, unit: 'MINUTES') {
                waitForQualityGate abortPipeline: true
                 }
              }
           }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} .'
            }
        }
        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword (
                credentialsId: 'dockerhub-credentials',
                usernameVariable: 'DOCKERHUB_USER',
                passwordVariable: 'DOCKERHUB_TOKEN'
               )] ) {
                      sh '''
                         echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
                         docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}
                         docker logout
                      '''
                    }
              }
         }



         stage('Deployment to Kubernetes'){
             steps{
                 sh '''
                    kubectl apply -f k8s/helpdesk-deployment.yaml 
                    kubectl apply -f k8s/helpdesk-service.yaml
                    kubectl apply -f k8s/helpdesk-ingress.yaml

                    kubectl set image deployment/helpdesk-app helpdesk-app-container=${DOCKERHUB_REPO}:${IMAGE_TAG} \
                      -n helpdesk

                    kubectl rollout status deployment/helpdesk-app -n helpdesk
                    '''

            }
        }
    }
}
