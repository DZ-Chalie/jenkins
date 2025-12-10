pipeline {
    agent { label 'app-184' }

    environment {
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'
        IMAGE_NAME_STRING = 'frontend,backend'
        CREDENTIAL_ID = 'harbor-login'

        SONARQUBE_URL = 'http://192.168.0.181:9000'
        SONARQUBE_TOKEN = 'sqa_4ca398bbb038ee6fb87aefd540c22ac980f55e8c'
        SONARQUBE = 'SonarQube'

        IMAGE_TAG = ''
    }

    stages {
        stage('SCM') { steps { checkout scm } }

        stage('Calculate Version') {
            steps {
                script {
                    def buildNum = currentBuild.number
                    def verCalc = String.format("%.1f", buildNum.toInteger() * 0.1)
                    env.IMAGE_TAG = "v${verCalc}"
                    echo "🎉 이번 빌드 버전은 [ ${env.IMAGE_TAG} ] 입니다."
                }
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // Docker 이미지 빌드 및 푸시 로직
                        sh "docker build -t ${fullImageName} -f Dockerfile.${image} SourceCode"

                        withCredentials([usernamePassword(credentialsId: CREDENTIAL_ID, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                            sh "docker login ${REGISTRY} -u \$USER -p \$PASS"
                            sh "docker push ${fullImageName}"
                        }
                        echo "✅ ${fullImageName} 푸시 완료"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // SSH를 통한 CD (181 서버에 배포)
                        sshagent(['my-ssh-key-id']) {
                            
                            // 👇 배포 서버 IP를 192.168.0.184로 수정합니다. (웹 실행 공간)
                            def deployHost = '192.168.0.184' 
                            def deployUser = 'kevin'

                            // ⭐ 중요 수정: 포트 충돌 회피 (8080 대신 8082 사용)
                            // 181 서버의 8080은 Jenkins가 사용 중
                            def port = (image == 'frontend') ? '8082' : '8081' 

                            // 기존 컨테이너 중지 및 삭제
                            sh "ssh ${deployUser}@${deployHost} 'docker stop my-${image}-server || true'"
                            sh "ssh ${deployUser}@${deployHost} 'docker rm my-${image}-server || true'"
                            sh "ssh ${deployUser}@${deployHost} 'docker pull ${fullImageName}'"

                            // 새 컨테이너 실행 (-p 8082:8080 또는 -p 8081:8080)
                            sh "ssh ${deployUser}@${deployHost} 'docker run -d -p ${port}:8080 --name my-${image}-server ${fullImageName}'"
                        }
                        echo "🚀 ${image} 배포 완료"
                    }
                }
            }
        }
    }
}
