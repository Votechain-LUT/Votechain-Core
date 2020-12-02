pipeline {
  environment {
    version = '0.0.'
    image = ''
    registry = 'ghcr.io/votechain-lut/core-api'
    ghcr_user = '210342'
    ghcr_access_token = credentials('ghcr-access-token')
  }
  agent any
  stages {
    stage('Build core api') {
      steps {
        script {
          image = docker.build(registry + ":" + version + BUILD_NUMBER, './src')
        }
      }
    }
    stage('Publish core api') {
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
