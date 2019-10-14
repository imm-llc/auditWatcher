pipeline{
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '3'))
    }

    triggers {
        cron('*/15 * * * *')
    }

    stages{
        stage("Install requirements"){
            steps{
                script{
                    echo "**********************************************"
                    echo ""
                    sh "/usr/local/bin/pip3 install --user -r reqs.txt"
                    echo ""
                    echo "**********************************************"
                }
            }
        }
        stage("Run Checks"){
            steps{
                withCredentials(
                    [
                        file(credentialsId: 'O365_KEY', variable: 'keyFile'),
                        file(credentialsId: 'O365_CONFIG', variable: 'configFile')
                    ]
                ){
                    script{
                        sh '''
                            cp $keyFile ./key.key
                            cp $configFile ./conf.json
                            chmod +x logs.py
                            ./logs.py conf.json
                        '''
                    }
                }
                
            }
        }
    }
    post{
        always{
            sh '''
            rm -f ./key.key
            rm -f ./conf.json
            '''
        }
        success{
            echo "========pipeline executed successfully ========"
        }
        failure{
            slackSend (color: "danger", message: "FAILURE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}")
        }
    }
}
