pipeline {
    agent { label 'app-184' }  // 184 서버에서 실행

    stages {
        stage('SCM') {
            steps {
                checkout scm
            }
        }

        stage('Calculate Version') {
            steps {
                script {
                    // 빌드 번호를 String으로 직접 변환하여 오류 방지
                    def buildNum = currentBuild.number
                    def verCalc = String.format("%.1f", buildNum.toInteger() * 0.1)
                    
                    env.IMAGE_TAG = "v${verCalc}"

                    echo "🎉 이번 빌드 버전은 [ ${env.IMAGE_TAG} ] 입니다."
                }
            }
        }
        
        stage('Simple Test') {
            steps {
                // index.html 파일이 제대로 체크아웃되었는지 확인
                sh 'ls -l index.html' 
                sh 'echo "✅ 파이프라인 기본 테스트 성공!"'
            }
        }
    }
}
