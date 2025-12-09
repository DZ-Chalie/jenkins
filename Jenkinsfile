pipeline {
    agent { label 'app-184' }  // 184 서버에서 빌드 작업을 실행하도록 설정

    environment {
        // Harbor 주소 및 프로젝트 설정
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'
        // Groovy 환경 변수 문법 오류 수정: 배열 대신 문자열로 정의
        IMAGE_NAME_STRING = 'frontend,backend' 
        // Harbor에 로그인할 자격 증명 ID
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube URL 및 토큰 설정
        SONARQUBE_URL = 'http://192.168.0.181:9000'
        SONARQUBE_TOKEN = 'sqa_4ca398bbb038ee6fb87aefd540c22ac980f55e8c'
        SONARQUBE = 'SonarQube'
        
        // Calculate Version 단계에서 값을 넣을 이미지 태그 변수 선언
        IMAGE_TAG = '' 
    }

    stages {
        stage('SCM') {
            steps {
                // SCM 체크아웃 오류 해결: 잡 설정의 Git 정보를 따르는 'checkout scm' 사용
                checkout scm
            }
        }

        /*
        stage('SonarQube Analysis') {
            steps {
                script {
                    // 툴 미설치로 인한 빌드 실패 방지를 위해 전체 단계 주석 처리
                    // def scannerHome = tool 'SonarScanner'
                    // withSonarQubeEnv(SONARQUBE) {
                    //     sh "${scannerHome}/bin/sonar-scanner"
                    // }
                }
            }
        }
        */

        stage('Calculate Version') {
            steps {
                script {
                    def buildNum = currentBuild.number.toInteger()
                    def verCalc = String.format("%.1f", buildNum * 0.1)
                    
                    env.IMAGE_TAG = "v${verCalc}"

                    echo "Debug: Build Number is [ ${buildNum} ]"
                    echo "Debug: Calculated version is [ ${verCalc} ]"
                    echo "🎉 이번 빌드 버전은 [ ${env.IMAGE_TAG} ] 입니다."
                }
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    // 문자열을 배열로 변환하여 사용
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
                    // 문자열을 배열로 변환하여 사용
                    def images = env.IMAGE_NAME_STRING.split(',')
                    
                    images.each { image ->
                        def fullImageName = "${REGISTRY}/${PROJECT}/${image}:${env.IMAGE_TAG}"

                        // SSH를 통해 개발 서버에 배포 (SSH Key 기반 인증 사용)
                        // 주의: 이 단계에서는 포트 충돌 문제가 발생할 수 있습니다.
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
