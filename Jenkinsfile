pipeline{
    agent any

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
                            ls -l
                        '''
                    }
                }
                
            }
        }
    }
    post{
        always{
            echo "========always========"
        }
        success{
            echo "========pipeline executed successfully ========"
        }
        failure{
            echo "========pipeline execution failed========"
        }
    }
}