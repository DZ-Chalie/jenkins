pipeline {
    agent { label 'app-184' }  // 184 서버에서 빌드 작업을 실행하도록 설정

    environment {
        // Harbor 주소 및 프로젝트 설정
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'
        // Docker 이미지 이름 (frontend, backend)
        IMAGE_NAME = "frontend,backend"  // 배열을 문자열로 수정
        // Harbor에 로그인할 자격 증명 ID
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube URL 및 토큰 설정
        SONARQUBE_URL = 'http://192.168.0.181:9000'  // SonarQube 서버 주소
        SONARQUBE_TOKEN = 'your-sonarqube-token'  // SonarQube 토큰
        SONARQUBE = 'SonarQube'  // SonarQube 서버 이름
    }

    stages {
        stage('SCM') {
            steps {
                // GitHub에서 소스 코드 체크아웃
                git 'https://github.com/DZ-Chalie/jenkins.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    // SonarQube 분석 실행
                    def scannerHome = tool 'SonarScanner'  // SonarQube Scanner 경로
                    withSonarQubeEnv(SONARQUBE) {  // SonarQube 환경 설정
                        sh "${scannerHome}/bin/sonar-scanner"  // SonarQube 분석 실행
                    }
                }
            }
        }

        stage('Calculate Version') {
            steps {
                script {
                    // 현재 빌드 번호 가져오기
                    def buildNum = currentBuild.number.toInteger()

                    // 버전 계산 (예: 1 -> v0.1)
                    def verCalc = String.format("%.1f", buildNum * 0.1)

                    // 환경 변수에 버전 저장
                    env.IMAGE_TAG = "v${verCalc}"

                    echo "🎉 이번 빌드 버전은 [ ${env.IMAGE_TAG} ] 입니다."
                }
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    // 각 이미지에 대해 빌드 및 푸시
                    def images = IMAGE_NAME.split(",")  // "frontend,backend"를 배열로 분리
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
                    // 각 이미지에 대해 배포 작업 실행
                    def images = IMAGE_NAME.split(",")  // "frontend,backend"를 배열로 분리
                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // SSH를 통해 개발 서버에 배포 (SSH Key 기반 인증 사용)
                        sshagent(['my-ssh-key-id']) {
                            // Docker 이미지를 개발 서버에서 풀하고 실행
                            sh "ssh user@192.168.0.184 'docker pull ${fullImageName}'"
                            sh "ssh user@192.168.0.184 'docker run -d -p 8080:80 --name my-${image}-server ${fullImageName}'"
                        }

                        echo "🚀 ${image} 배포 완료"
                    }
                }
            }
        }
    }
}
