pipeline {
    agent { label 'app-184' }  // 184 서버에서 빌드 작업을 실행하도록 설정

    environment {
        // Harbor 주소 및 프로젝트 설정
        REGISTRY = 'harbor.local.net'
        PROJECT = 'charlie'
        // Docker 이미지 이름 (frontend, backend)
        IMAGE_NAME = ["frontend", "backend"]  // 배열을 다시 배열로 수정 (수정한 부분)
        
        // Harbor에 로그인할 자격 증명 ID
        CREDENTIAL_ID = 'harbor-login'

        // SonarQube URL 및 토큰 설정
        SONARQUBE_URL = 'http://192.168.0.181:9000'  // SonarQube 서버 주소
        SONARQUBE_TOKEN = 'sqa_4ca398bbb038ee6fb87aefd540c22ac980f55e8c'  // SonarQube 토큰 (수정한 부분)
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
    }
}

