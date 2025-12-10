pipeline {
    // Pipeline이 실행될 Jenkins Agent 지정 (184 서버)
    agent { label 'app-184' }

    environment {
        // Harbor 주소 및 프로젝트 설정
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'

        // 이미지 이름 (Docker Build에 사용)
        IMAGE_NAME_STRING = 'frontend,backend'

        // Harbor에 로그인할 자격 증명 ID
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube 서버 정보 (181 서버)
        SONARQUBE_URL = 'http://192.168.0.181:9000'
        SONARQUBE_TOKEN = 'sqa_4ca398bbb038ee6fb87aefd540c22ac980f55e8c'
        SONARQUBE_SERVER_ID = 'sonarqube-local' // Jenkins 설정에 정의된 SonarQube 서버 이름

        // 이미지 태그 변수 선언
        IMAGE_TAG = ''
    }

    stages {
        stage('SCM') {
            steps {
                echo "--- 1. Git Repository Checkout ---"
                checkout scm
            }
        }
        
        // SonarQube 분석 스테이지
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "--- 2. SonarQube Code Analysis Started ---"
                    // Jenkins Agent에 Java 17 경로를 설정하여 SonarScanner 실행 준비
                    withEnv(['JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64']) {
                        withSonarQubeEnv(env.SONARQUBE_SERVER_ID) {
                            def scannerHome = tool 'SonarScanner'
                            // SonarScanner 실행
                            sh "export JAVA_HOME=${JAVA_HOME} && ${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=charlie-monorepo -Dsonar.sources=."
                        }
                    }
                }
            }
        }

        stage("Quality Gate Check") {
            steps {
                script {
                    echo "--- 3. Waiting for SonarQube Quality Gate Result (Max 5 mins) ---"
                    timeout(time: 5, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        // 이미지 버전 계산 및 설정 (빌드 번호 기반)
        stage('Calculate Version') {
            steps {
                script {
                    // ✅ 수정: env.BUILD_NUMBER를 사용하여 안정적인 버전 태그 생성
                    env.IMAGE_TAG = "v1.${env.BUILD_NUMBER}"
                    // ✅ 수정: echo 명령에서 변수 값을 출력하도록 수정
                    echo "🎉 이번 빌드 버전은 [ ${env.IMAGE_TAG} ] 입니다."
                }
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    echo "--- 4. Build and Push to Harbor ---"
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // Docker 빌드 (빌드 컨텍스트: SourceCode)
                        sh "docker build -t ${fullImageName} -f Dockerfile.${image} SourceCode"

                        // Docker 로그인 및 푸시
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
                    echo "--- 5. Deploy to Dev Server (184) ---"
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // ⭐ SSH 사용하지 않고 184 Agent 로컬에서 직접 Docker 제어

                        // 컨테이너 중지 및 삭제 (|| true로 컨테이너가 없어도 성공)
                        sh "docker rm -f my-${image}-server || true"

                        // 이미지 다운로드
                        sh "docker pull ${fullImageName}"

                        // 포트 설정: 8080은 Jenkins가 사용하므로 frontend는 8082로 설정
                        def port = (image == 'frontend') ? '8082' : '8081'

                        // 새 컨테이너 실행
                        sh "docker run -d -p ${port}:8080 --name my-${image}-server ${fullImageName}"

                        echo "🚀 ${image} 배포 완료 (Dev Server: 192.168.0.184:${port})"
                    }
                }
            }
        }
    }
}
