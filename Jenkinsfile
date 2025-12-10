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

        // 이미지 태그 변수 선언 (Calculate Version에서 설정)
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
                    withEnv(['JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64']) {
                        withSonarQubeEnv(env.SONARQUBE_SERVER_ID) {
                            def scannerHome = tool 'SonarScanner'
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

        // 🌟 새로 추가: 통합 테스트 스테이지
        stage('Integration Test') {
            steps {
                echo "--- 4. Integration Tests Started (API/E2E Test) ---"
                // frontend 디렉토리로 이동하여 npm install 후 npm test 스크립트 실행
                // ❗ package.json에 test 스크립트 추가 필요 (이미 Git에 커밋함)
                sh "cd SourceCode/frontend && npm install && npm test"
                echo "✅ Integration Tests Passed."
            }
        }

        stage('Calculate Version') {
            steps {
                script {
                    echo "--- Calculating Build Version ---"
                    // 🚨 최종 수정 (readFile 방식 적용): 셸 출력을 파일에 저장하여 Groovy 변수 스코프 문제를 우회합니다.
                    sh "echo v1.${BUILD_NUMBER} > .build_version"

                    // Groovy가 파일을 읽어 환경 변수에 할당합니다.
                    env.IMAGE_TAG = readFile('.build_version').trim()
                }
                echo "🎉 이번 빌드 버전은 [ ${env.IMAGE_TAG} ] 입니다."
            }
        }

        stage('Build, Scan & Push') {
            steps {
                script {
                    echo "--- 5. Build, Scan with Trivy, and Push to Harbor ---"
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // 5-1. Docker 이미지 빌드
                        sh "docker build -t ${fullImageName} -f Dockerfile.${image} SourceCode"

                        // 5-2. 🚀 Trivy 보안 스캔
                        echo "--- Trivy Security Scan for ${image} Started ---"
                        def trivyImage = "${fullImageName}"

                        // 🌟 Trivy 보안 게이트 복구: CRITICAL 취약점 발견 시 Exit Code 1 반환
                        def scan_command = "trivy image --severity CRITICAL --exit-code 1 --format table ${trivyImage}"

                        try {
                            sh scan_command
                            echo "✅ Trivy Scan Passed for ${image}. Security Gate is GREEN."
                        } catch (e) {
                            // Trivy가 Exit Code 1을 반환하면 Jenkins 빌드 실패 처리
                            error "🚨 Trivy Scan Failed for ${image}: CRITICAL vulnerabilities detected. Fix Dockerfile and redeploy."
                        }

                        // 5-3. Docker 로그인 및 푸시 (Trivy 스캔 통과 시에만 실행)
                        withCredentials([usernamePassword(credentialsId: CREDENTIAL_ID, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                            sh "docker login ${REGISTRY} -u \$USER -p \$PASS"
                            sh "docker push ${fullImageName}"
                        }
                        echo "✅ ${fullImageName} 푸시 완료"
                    }
                }
            }
        }

        // 🌟 스테이지 이름 변경: Deploy to Dev
        stage('Deploy to Dev') {
            steps {
                script {
                    echo "--- 6. Deploy to Dev Server (184) ---"
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

        // 🌟 새로 추가: 운영 환경 배포 및 수동 승인
        stage('Deploy to Production') {
            steps {
                script {
                    // 수동 승인 단계 (운영 배포 전 관리자 확인)
                    timeout(time: 1, unit: 'HOURS') {
                        input message: 'QA 및 개발 배포 테스트 완료! Production 배포를 승인하시겠습니까?', submitter: 'admin'
                    }

                    echo "--- 7. Deploy to Production Server ---"
                    def images = env.IMAGE_NAME_STRING.split(',')

                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // ❗ 이 부분은 운영 서버의 실제 IP와 배포 로직으로 대체해야 합니다.
                        // 예시: sh "ssh user@prod-server 'docker pull ${fullImageName} && docker run...'"
                        echo "🚀 ${image} 배포 준비 완료 (Production Server)"
                    }
                }
            }
        }
    }
}
