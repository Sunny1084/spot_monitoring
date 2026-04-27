# Jenkins Pipeline Setup Guide

This guide walks you through setting up a Jenkins pipeline for the Spot Monitoring project.

## Prerequisites

- Jenkins installed and running at `http://localhost:8080`
- Git installed
- Python 3.11+ installed
- Docker installed and running
- GitHub repository created with your project

## Step 1: Prepare Jenkins Container

Your Jenkins is running in a Docker container without Python 3 and Docker CLI. Install dependencies:

### Option A: Using Setup Script (Recommended)

1. The repository includes `jenkins-setup.sh`:
   ```bash
   docker exec jenkins bash /var/jenkins_home/jenkins-setup.sh
   ```

2. Wait for installation to complete

3. Verify:
   ```bash
   docker exec jenkins python3 --version
   docker exec jenkins docker --version
   ```

### Option B: Manual Installation

Access Jenkins container:
```bash
docker exec -it jenkins bash
```

Run these commands inside the container:
```bash
apt-get update
apt-get install -y python3 python3-venv python3-pip git

# Install Docker CLI
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add jenkins user to docker group
usermod -aG docker jenkins
```

Exit the container:
```bash
exit
```

Restart Jenkins:
```bash
docker restart jenkins
```

## Step 2: Create a New Jenkins Job

1. Open Jenkins: `http://localhost:8080`
2. Click **New Item**
3. Enter job name: `spot-monitoring-pipeline`
4. Select **Pipeline**
5. Click **OK**

## Step 3: Configure the Pipeline

In the job configuration page:

### 3.1 General Settings
- Check **GitHub project**
- Project URL: `https://github.com/Sunny1084/spot_monitoring/`

### 3.2 Build Triggers
- Check **GitHub hook trigger for GITScm polling**
- This will trigger builds on every push to GitHub

### 3.3 Advanced Project Options
- Leave defaults or customize as needed

### 3.4 Pipeline Definition

Select **Pipeline script from SCM**:

- **SCM**: Git
- **Repository URL**: `https://github.com/Sunny1084/spot_monitoring.git`
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

### Issue: "Batch scripts can only be run on Windows nodes"
- Your Jenkins is running on Linux, not Windows
- The Jenkinsfile has been updated to use `sh` commands for Linux
- Ensure you commit and push the updated Jenkinsfile:
  ```powershell
  git add Jenkinsfile
  git commit -m "Update Jenkinsfile for Linux Jenkins agent"
  git push origin main
  ```

### Issue: "Python not found" (Linux)
- Ensure Python 3 is installed on the Jenkins server
- SSH into Jenkins container and install:
  ```bash
  apt-get update && apt-get install -y python3 python3-venv
  ```
- Or specify full path in pipeline: `/usr/bin/python3`

### Issue: "Docker daemon is not running"
- Ensure Docker is running on Jenkins server or agent
- Check Jenkins agent configuration in Jenkins UI
- Verify Docker socket permissions in Jenkins container:
  ```bash
  sudo usermod -aG docker jenkins
  sudo systemctl restart jenkins
  ```

### Issue: "venv command not found" (Linux)
- Install Python3 venv:
  ```bash
  apt-get install -y python3.11-venv
  ```
- Or use: `python3 -m venv venv`

### Issue: Test container fails to start
- Check if port 8000 is already in use:
  ```bash
  docker ps -a
  docker stop test-container || true
  docker rm test-container || true
  ```

## Jenkins Running on Linux

The Jenkinsfile is now configured for Linux Jenkins agents running as Docker containers.

### Key Differences from Windows:
- Uses `sh` instead of `bat` for shell commands
- Venv activation: `. venv/bin/activate` instead of `call venv\Scripts\activate.bat`
- Path separators: `/` instead of `\`
- Docker socket: `/var/run/docker.sock` instead of `npipe`

### Accessing Jenkins Container

If Jenkins is running in Docker:

```bash
docker exec -it jenkins bash
```

### Installing Dependencies in Jenkins Container

```bash
docker exec jenkins apt-get update
docker exec jenkins apt-get install -y python3 python3-venv docker.io git
```

## Linux-Specific Pipeline Example

The updated Jenkinsfile uses shell commands compatible with Linux:

```groovy
sh '''
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
'''
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
