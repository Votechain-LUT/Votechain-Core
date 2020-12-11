pipeline {
  environment {
    version = '0.0.'
    image = ''
    registry = 'ghcr.io/votechain-lut/core-api'
    ghcr_user = '210342'
    ghcr_access_token = credentials('ghcr-access-token')
    private_api_key = credentials('private-api-key')
  }
  agent any
  stages {
    stage('Build core api') {
      steps {
        script {
          image = docker.build(registry + ":" + version + BUILD_NUMBER, '--build-arg PRIVATE_KEY=$private_api_key ./src')
        }
      }
    }
    stage('Static code analysis') {
      steps {
        script {
          image.inside {
            script {
              sh 'pylint --rcfile=pylintrc --output-format=parseable --reports=n --exit-zero src/votechain > pylint-votechain.log'
              sh 'pylint --rcfile=pylintrc --output-format=parseable --reports=n --exit-zero src/core > pylint-core.log'
              sh 'cat pylint-votechain.log pylint-core.log'
              sh 'cat pylint-votechain.log | grep "rated at" | grep -Eo "([7-9]|10)" | head -1 | grep -Eq "([7-9]|10)"'
              sh 'cat pylint-core.log | grep "rated at" | grep -Eo "([7-9]|10)" | head -1 | grep -Eq "([7-9]|10)"'
            }
          }
        }
      }
    }
    stage('Unit tests') {
      steps {
        script {
          image.inside {
            script {
              sh 'export PRIVATE_KEY=$private_api_key'
              sh 'python3 src/manage.py test'
            }
          }
        }
      }
    }
    stage('Publish core api') {
      when {
        branch 'main'
      }
      steps {
        sh '''#!/bin/bash
          echo $ghcr_access_token | docker login ghcr.io -u $ghcr_user --password-stdin
        '''
        script {
          image.push()
        }
      }
    }
  }
}
