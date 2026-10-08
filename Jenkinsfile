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

        stage('Test and Code Coverage') {
           steps {

                 withCredentials([string(
                       credentialsId: 'postgres_local_db_password',
                       variable: 'DB_PASSWORD'
                   )]) {
                      sh '''
                           export FLASK_SECRET_KEY="test-secret-key"
                           python3 -m venv .venv
                           .venv/bin/pip install -r requirements.txt
                           .venv/bin/pytest --cov=app \
                                            --cov-report=term-missing \
                                            --cov-report=xml

                         '''
                 }

              }
         }
        stage('SonarQube Scan') {
           steps {
             script {
                def scannerHome = tool 'sonar-scanner'
                withSonarQubeEnv('sonarqube-helpdesk') {
                  sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=helpdesk-app -Dsonar.sources=. -Dsonar.exclusions=tests/**"

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



         stage('Helm chart deployment'){
             steps{
                 sh '''
                       helm upgrade helpdesk ./helm/helpdesk -n helpdesk \
                       --set image.tag=${IMAGE_TAG}

                '''

            }
        }
    }
}
