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

        // SonarQube 서버 정보 (withSonarQubeEnv에 필요한 ID 정의)
        SONARQUBE_URL = 'http://192.168.0.181:9000'
        SONARQUBE_TOKEN = 'sqa_4ca398bbb038ee6fb87aefd540c22ac980f55e8c'
        
        // 🚨 Jenkins 시스템 설정에서 정의한 SonarQube 서버 이름
        SONARQUBE_SERVER_ID = 'sonarqube-local' 

        // 이미지 태그 변수 선언
        IMAGE_TAG = ''
    }

    stages {
        stage('SCM') {
            steps {
                echo "--- 1. Git Repository Checkout ---"
                // 잡 설정의 Git 정보를 따르는 'checkout scm' 사용
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "--- 2. SonarQube Code Analysis Started ---"
                    // Jenkins 시스템 설정에서 정의한 SonarQube 서버 이름 사용
                    withSonarQubeEnv(env.SONARQUBE_SERVER_ID) { 
                        // 🚨 'SonarScanner' 사용 (고객님의 설정에 맞춰 수정)
                        sh "${tool 'SonarScanner'} -Dsonar.projectKey=charlie-monorepo -Dsonar.sources=."
                    }
                }
            }
        }
        
        stage("Quality Gate Check") {
            steps {
                script {
                    echo "--- 3. Waiting for SonarQube Quality Gate Result (Max 5 mins) ---"
                    timeout(time: 5, unit: 'MINUTES') {
                        // quality gate 결과가 'OK'가 아닐 경우 파이프라인 중단
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Calculate Version') {
            steps {
                script {
                    def buildNum = currentBuild.number.toInteger()
                    // 버전 계산 수정 (v1. 빌드번호)
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

                        // Docker 이미지 빌드
                        sh "docker build -t ${fullImageName} -f Dockerfile.${image} ."

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
                        sh "docker run -d -p 8080:80 --name my-${image}-server ${fullImageName}"
                        
                        echo "🚀 ${image} 배포 완료 (Dev Server: 192.168.0.184)"
                    }
                }
            }
        }
    }
}
