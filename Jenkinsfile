pipeline {
    agent any

    environment {
        IMAGE_NAME = "spot-monitoring-api"
        PYTHON_VERSION = "3.11"
        GIT_REPO = "https://github.com/your-username/spot_monitoring.git"
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
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    pytest tests/ -v --cov=src --cov-report=xml
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo 'Training anomaly detection model...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    python -m src.pipelines.train_pipeline
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat '''
                    docker build -t %IMAGE_NAME%:latest .
                    docker tag %IMAGE_NAME%:latest %IMAGE_NAME%:${BUILD_NUMBER}
                '''
            }
        }

        stage('Run Container Tests') {
            steps {
                echo 'Testing Docker container...'
                bat '''
                    docker run --rm -d -p 8000:8000 --name test-container %IMAGE_NAME%:latest
                    timeout /t 5 /nobreak
                    docker logs test-container
                    docker stop test-container
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deployment stage - customize as needed'
                bat '''
                    echo Container is ready for deployment
                    docker image ls | findstr %IMAGE_NAME%
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
        }
        unstable {
            echo 'Pipeline is unstable'
        }
    }
}
