pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '241533118928'
        AWS_REGION     = 'us-east-1'
        IMAGE_REPO     = 'my-devops-app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
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
                    echo "Running Code Quality Checks..."
                    
                    sh "pip install flake8"                  
                    
                    sh "flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics"
                    
                    echo "Tests Passed! Code is clean."
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
                    // Authenticate Docker to ECR
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}"
                    // Push the image
                    sh "docker push ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh-key']) { // 'ec2-ssh-key' is the ID of your stored SSH private key in Jenkins
                    sh """
                    ssh -o StrictHostKeyChecking=no ubuntu@your-ec2-ip << EOF
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}
                        docker pull ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}
                        docker stop my-app || true
                        docker rm my-app || true
                        docker run -d --name my-app -p 80:5000 ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}
                    EOF
                    """
                }
            }
        }
    }
}