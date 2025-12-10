pipeline {
    agent { label 'app-184' }

    environment {
        // Harbor 관련 환경 변수 재정의
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'
        // 현재 Git repo에는 frontend와 backend가 모두 존재하므로 두 개 모두 빌드
        IMAGE_NAME_STRING = 'frontend,backend'
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube는 CI/CD 진행을 위해 주석 처리 상태를 유지하거나 제거합니다.
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

                        // ⭐ 수정 1: Docker 이미지 빌드 컨텍스트를 'SourceCode' 디렉토리로 변경
                        sh "docker build -t ${fullImageName} -f Dockerfile.${image} SourceCode"

                        // Docker 로그인 및 푸시 (Harbor)
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
                            // 기존 컨테이너 중지 및 삭제 후 새로운 이미지로 재시작
                            sh "ssh kevin@192.168.0.181 'docker stop my-${image}-server || true'"
                            sh "ssh kevin@192.168.0.181 'docker rm my-${image}-server || true'"
                            sh "ssh kevin@192.168.0.181 'docker pull ${fullImageName}'"

                            // 프론트엔드는 8080, 백엔드는 8081 포트로 분리하여 포트 충돌 방지
                            def port = (image == 'frontend') ? '8080' : '8081'

                            // ⭐ 수정 2: 배포 시 포트 바인딩 로직 변경 (Deploy 단계는 수정 사항 없음, 확인용)
                            sh "ssh kevin@192.168.0.181 'docker run -d -p ${port}:8080 --name my-${image}-server ${fullImageName}'"
                        }
                        echo "🚀 ${image} 배포 완료"
                    }
                }
            }
        }
    }
}
