pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '241533118928'
        AWS_REGION     = 'us-east-1'
        IMAGE_REPO     = 'my-devops-app'
        IMAGE_TAG      = "${BUILD_NUMBER}"   // ✅ Fixed: no env. prefix needed here
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"  // ✅ Fixed
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test & Lint') {
            steps {
                script {
                    echo "Creating Virtual Environment and Running Lint..."
                    sh """
                        # 1. Create the virtual environment
                        python3 -m venv venv
                        
                        # 2. Install flake8 inside the venv
                        ./venv/bin/pip install flake8
                        
                        # 3. Run the linting test using the venv version of flake8
                        ./venv/bin/flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                    """
                    echo "Tests Passed!"
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_REPO}:${IMAGE_TAG} ."
                    sh "docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}"
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_URL}
                    """
                    sh "docker push ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@your-ec2-ip '
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                            docker pull ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}
                            docker stop my-app || true
                            docker rm my-app || true
                            docker run -d --name my-app -p 80:5000 ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}
                        '
                    """
                    // ✅ Fixed: heredoc << EOF doesn't work reliably in Jenkins sh
                    // Use single-quoted SSH command block instead
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully! Image: ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}"
        }
        failure {
            echo "❌ Pipeline failed. Check logs above."
        }
    }
}
