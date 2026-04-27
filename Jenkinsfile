pipeline {
    agent any

    environment {
        IMAGE_NAME = "spot-monitoring-api"
        PYTHON_VERSION = "3.11"
        GIT_REPO = "https://github.com/Sunny1084/spot_monitoring.git"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v --cov=src --cov-report=xml
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo 'Training anomaly detection model...'
                sh '''
                    . venv/bin/activate
                    python -m src.pipelines.train_pipeline
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${IMAGE_NAME}:latest .
                    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Run Container Tests') {
            steps {
                echo 'Testing Docker container...'
                sh '''
                    docker run --rm -d -p 8000:8000 --name test-container ${IMAGE_NAME}:latest
                    sleep 5
                    docker logs test-container
                    docker stop test-container || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deployment stage - customize as needed'
                sh '''
                    echo 'Container is ready for deployment'
                    docker image ls | grep ${IMAGE_NAME}
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed'
            archiveArtifacts artifacts: 'mlruns/**', allowEmptyArchive: true
            archiveArtifacts artifacts: 'artifacts/**', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
            sh 'docker stop test-container || true'
            sh 'docker rm test-container || true'
        }
        unstable {
            echo 'Pipeline is unstable'
        }
    }
}
