pipeline {
    // Pipeline이 실행될 Jenkins Agent 지정 (184 서버)
    agent { label 'app-184' }

    environment {
        // Harbor 관련 환경 변수
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'
        IMAGE_NAME_STRING = 'frontend,backend'
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube 설정 (181 서버)
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

        // 4. 배포 (CD) - 184 서버 (Agent)에서 로컬로 직접 Docker 제어
        stage('Deploy') {
            steps {
                script {
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // ⭐ SSH 블록 (sshagent) 완전히 제거됨
                        
                        // 포트 충돌 방지: frontend는 8082, backend는 8081 사용
                        def port = (image == 'frontend') ? '8082' : '8081' 

                        // 기존 컨테이너 중지 및 삭제 (로컬 명령으로 실행)
                        sh "docker stop my-${image}-server || true"
                        sh "docker rm my-${image}-server || true"
                        
                        // 이미지 다운로드 (로컬에서 pull)
                        sh "docker pull ${fullImageName}"

                        // 새 컨테이너 실행 (로컬 명령으로 실행)
                        sh "docker run -d -p ${port}:8080 --name my-${image}-server ${fullImageName}"
                        
                        echo "🚀 ${image} 배포 완료"
                    }
                }
            }
        }
    }
}
