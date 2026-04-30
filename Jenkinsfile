pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID  = '241533118928'
        AWS_REGION      = 'us-east-1'
        IMAGE_REPO      = 'my-devops-app'
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        ECR_URL         = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        EC2_INSTANCE_ID = 'i-04d9dbcba5a128abd'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test & Lint') {
            steps {
                sh '''
                    python3 -m pip install --user flake8
                    python3 -m flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
                echo "✅ Code Quality Check Passed!"
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    docker build -t ${IMAGE_REPO}:${IMAGE_TAG} .
                    docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}
                """
            }
        }

        stage('Push to ECR') {
            steps {
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_URL}

                    docker push ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy to EC2 via SSM') {
            steps {
                sh """
                    aws ssm send-command \
                        --region ${AWS_REGION} \
                        --instance-ids ${EC2_INSTANCE_ID} \
                        --document-name "AWS-RunShellScript" \
                        --comment "Deploy build ${IMAGE_TAG}" \
                        --parameters 'commands=[
                            "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URL}",
                            "docker pull ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}",
                            "docker stop my-app || true",
                            "docker rm my-app || true",
                            "docker run -d --name my-app -p 80:5000 ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG}"
                        ]' \
                        --output text
                """
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful! Build #${env.BUILD_NUMBER} is live."
        }
        failure {
            echo "❌ Pipeline failed at build #${env.BUILD_NUMBER}. Check logs."
        }
        always {
            sh """
                docker rmi ${IMAGE_REPO}:${IMAGE_TAG} || true
                docker rmi ${ECR_URL}/${IMAGE_REPO}:${IMAGE_TAG} || true
            """
        }
    }
}
