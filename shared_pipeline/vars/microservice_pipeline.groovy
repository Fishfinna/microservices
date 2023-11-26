def call(imageName) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage('Lint') {
                steps {
                    sh "pylint --fail-under=5.0 *.py"
                }
            }
            stage('Security Check') {
                script {
                    sh 'pip install safety --break-system-packages'
                    sh 'safety check -r requirements.txt --full-report'
                }
            }
            stage('Package') {
                steps {
                    withCredentials([string(credentialsId: 'ShantiDockerHub', variable: 'TOKEN')]) {
                        sh "docker login -u 'fishfinna' -p '$TOKEN' docker.io"
                        sh "docker build -t ${imageName}:latest --tag fishfinna/${imageName}:${imageName} ."
                        sh "docker push fishfinna/${dockerRepoName}:${imageName}"
                    } 
                }
            }
            stage("Deploy") {
                when {
                    expression { params.DEPLOY }
                }
                steps {
                    sshagent(credentials: ['shanti-kafka-ssh']) {
                        sh "ssh azureuser@20.151.78.202 'cd ~/microservices/deployment && docker-compose pull && docker-compose up -d'"
                    }
                }
            }
        }
    }
}