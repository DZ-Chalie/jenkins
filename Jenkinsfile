pipeline {
    // 빌드 에이전트 설정 (184 서버)
    agent { label 'app-184' }

    environment {
        // Harbor 주소 및 프로젝트 설정
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'

        // 이미지 이름 (Docker Build에 사용)
        IMAGE_NAME_STRING = 'frontend,backend'

        // Harbor에 로그인할 자격 증명 ID
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube 서버 정보
        SONARQUBE_URL = 'http://192.168.0.181:9000'
        SONARQUBE_TOKEN = 'sqa_4ca398bbb038ee6fb87aefd540c22ac980f55e8c'

        // Jenkins 시스템 설정에서 정의한 SonarQube 서버 이름
        SONARQUBE_SERVER_ID = 'sonarqube-local'

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

        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "--- 2. SonarQube Code Analysis Started ---"
                    // 확인된 Java 17 경로를 사용하여 JAVA_HOME 설정
                    withEnv(['JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64']) {
                        withSonarQubeEnv(env.SONARQUBE_SERVER_ID) {
                            def scannerHome = tool 'SonarScanner'
                            // JAVA_HOME을 환경 변수로 전달하고 SonarScanner를 실행
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

        stage('Calculate Version') {
            steps {
                script {
                    // 🚨 수정: currentBuild.number를 String으로 변환하여 null 방지 및 확실한 할당
                    def buildNum = currentBuild.number.toString()
                    env.IMAGE_TAG = "v1.${buildNum}"
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

                        // 🚨 수정: Docker 빌드 컨텍스트를 '.'에서 'SourceCode'로 변경 (파일을 찾기 위함)
                        // Dockerfile 경로는 그대로 유지 (Dockerfile.{image}는 Jenkins Workspace 루트에 위치한다고 가정)
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

                        // 기존 컨테이너 중지 및 삭제 (재배포 시 필수)
                        sh "docker rm -f my-${image}-server || true"

                        // Docker 이미지를 개발 서버에서 풀하고 실행 (184 서버 로컬에서 실행)
                        sh "docker pull ${fullImageName}"

                        def port = (image == 'frontend') ? '8082' : '8081'
                        sh "docker run -d -p ${port}:8080 --name my-${image}-server ${fullImageName}"

                        echo "🚀 ${image} 배포 완료 (Dev Server: 192.168.0.184)"
                    }
                }
            }
        }
    }
}
