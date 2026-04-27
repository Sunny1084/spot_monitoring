# Jenkins Pipeline Setup Guide

This guide walks you through setting up a Jenkins pipeline for the Spot Monitoring project.

## Prerequisites

- Jenkins installed and running at `http://localhost:8080`
- Git installed
- Python 3.11+ installed
- Docker installed and running
- GitHub repository created with your project

## Step 1: Create a New Jenkins Job

1. Open Jenkins: `http://localhost:8080`
2. Click **New Item**
3. Enter job name: `spot-monitoring-pipeline`
4. Select **Pipeline**
5. Click **OK**

## Step 2: Configure the Pipeline

In the job configuration page:

### 2.1 General Settings
- Check **GitHub project**
- Project URL: `https://github.com/your-username/spot_monitoring/`

### 2.2 Build Triggers
- Check **GitHub hook trigger for GITScm polling**
- This will trigger builds on every push to GitHub

### 2.3 Advanced Project Options
- Leave defaults or customize as needed

### 2.4 Pipeline Definition

Select **Pipeline script from SCM**:

- **SCM**: Git
- **Repository URL**: `https://github.com/your-username/spot_monitoring.git`
- **Credentials**: Add GitHub credentials if private repo
- **Branch Specifier**: `*/main`
- **Script Path**: `Jenkinsfile`

This tells Jenkins to run the `Jenkinsfile` from your repository root.

### Alternative: Direct Jenkinsfile

If you want to paste the pipeline directly:
- Select **Pipeline script**
- Copy the content from your `Jenkinsfile` into the **Script** text area

## Step 3: Configure Jenkins System

1. Go to **Manage Jenkins** → **Configure System**
2. Scroll to **Python** section (if available) and set Python version
3. Scroll to **Git** section and configure Git executable path
4. Click **Save**

## Step 4: Install Required Plugins

1. Go to **Manage Jenkins** → **Manage Plugins** → **Available**
2. Search and install:
   - **GitHub Plugin**
   - **Pipeline Plugin** (usually pre-installed)
   - **Docker Pipeline**
   - **Cobertura Plugin** (for code coverage reports)

3. Restart Jenkins after installing plugins

## Step 5: Create GitHub Webhook (optional but recommended)

1. Go to your GitHub repo settings
2. Click **Webhooks** → **Add webhook**
3. Payload URL: `http://your-jenkins-server:8080/github-webhook/`
4. Content type: `application/json`
5. Events: **Push events**
6. Click **Add webhook**

Now Jenkins will automatically run the pipeline when you push to GitHub.

## Step 6: Run Your First Build

### Option A: Manual Trigger
1. Go to Jenkins job page
2. Click **Build Now**

### Option B: Automatic (on Git push)
1. Make a commit and push to GitHub
2. Jenkins will automatically trigger the pipeline

## Step 7: Monitor Pipeline Execution

1. Click on the build number (e.g., #1)
2. Click **Console Output** to view logs in real-time
3. Each stage shows:
   - Stage name
   - Start time
   - Duration
   - Status (success/failure)

## Step 8: View Test Reports and Artifacts

After a successful build:

1. Click on the build
2. **Artifacts** section shows:
   - `mlruns/` - MLflow experiment tracking
   - `artifacts/models/` - Trained model files

3. **Test Results** section shows:
   - pytest coverage reports (if Cobertura Plugin is installed)

## Troubleshooting

### Issue: "bat command not found"
- This script uses Windows batch (`bat`) commands
- Ensure Jenkins agent is running on Windows
- If using Linux agents, change `bat` to `sh` commands

### Issue: "Python not found"
- Add Python to Jenkins system PATH
- Or specify full path in pipeline: `C:\\Python311\\python.exe`

### Issue: "Docker daemon is not running"
- Start Docker Desktop before running pipeline
- Or configure Jenkins to run Docker commands via remote Docker daemon

### Issue: "venv command not found"
- Ensure you're using the correct Python installation
- Run: `python -m venv --version` to verify venv module availability

## Example Windows Batch Fixes

If `bat` commands fail, replace with:

```groovy
// For tests without venv
stage('Run Tests') {
    steps {
        bat 'pytest tests/ -v'
    }
}

// With full Python path
stage('Install Dependencies') {
    steps {
        bat '''
            C:\\Python311\\python.exe -m venv venv
            call venv\\Scripts\\activate.bat
            pip install -r requirements.txt
        '''
    }
}
```

## Pipeline Stages Explained

1. **Checkout Code**: Clones the repository
2. **Install Dependencies**: Creates venv and installs Python packages
3. **Run Tests**: Executes unit tests with coverage
4. **Train Model**: Runs the training pipeline
5. **Build Docker Image**: Creates Docker container image
6. **Run Container Tests**: Tests if Docker container runs
7. **Deploy**: Placeholder for deployment logic
8. **Post Actions**: Archives artifacts and reports

## Next Steps

1. Customize the `Jenkinsfile` for your deployment needs
2. Add email notifications on success/failure
3. Set up Jenkins agents on different machines
4. Integrate with monitoring tools (e.g., ELK stack, Prometheus)
5. Add security scanning stages (e.g., SonarQube)

## Useful Jenkins Links

- Pipeline Documentation: `http://localhost:8080/job/spot-monitoring-pipeline/pipeline-syntax/`
- Declarative Syntax: `http://localhost:8080/job/spot-monitoring-pipeline/pipeline-syntax/`
- Blue Ocean UI: `http://localhost:8080/blue/`

## Example: Monitoring the Pipeline

1. Use Blue Ocean: `http://localhost:8080/blue/`
2. Shows pipeline visualization
3. Easy to spot failed stages
4. Real-time log streaming
