// Jenkins multibranch pipeline geared towards building
// and deploying cf.gov production-like Docker stack.
// 
// This pipeline uses Jenkins Shared Libraries for several
// pipeline steps. For details on how those work, see
// GHE repo: app-ops/app-ops-jenkins-shared-libraries
pipeline {

    agent {
        label 'docker-agent'
    }

    environment {
        APP_NAME = "cf-gov"
        BASE_HOSTNAME = 'demo.cfpb.gov'
        IMAGE_REPO="cfpb/cfgov-python"
        IMAGE_TAG="${JOB_BASE_NAME}-${BUILD_NUMBER}"
        STACK_PREFIX = 'cfgov'
        DOCKER_REGISTRY = 'dtr.cfpb.gov'
        DOCKER_REGISTRY_URL = 'https://dtr.cfpb.gov/'
        DOCKER_REGISTRY_ORG = 'development'
    }

    parameters {
        booleanParam(
            name: 'DEPLOY',
            defaultValue: false,
            description: 'Deploy the stack?'
        )
    }

    options {
        ansiColor('xterm')
        parallelsAlwaysFailFast()
        timestamps()
    }
    
    stages {

        stage ('Init') {
            steps {
                script {
                    env.STACK_NAME = dockerStack.sanitizeStackName("${env.STACK_PREFIX}-${JOB_BASE_NAME}")
                    env.CFGOV_HOSTNAME = dockerStack.getHostingDomain(env.STACK_NAME)
                    env.IMAGE_NAME_LOCAL = "${env.IMAGE_REPO}:${env.IMAGE_TAG}"

                    // Site name
                    env.CFGOV_SITE_SCHEME = 'https'
                    env.CFGOV_SITE_DOMAIN = "appops-${STACK_NAME}.${BASE_HOSTNAME}"
                    env.CFGOV_SITE_URL = "${CFGOV_SITE_SCHEME}://${CFGOV_SITE_DOMAIN}"
                }
                sh 'env | sort'
            }
        }

        stage('Checkout') {
            steps {
                dir('static.in/cfgov-fonts') {
                    script {
                        git ghe.getRepoUrl('CFGOV/cfgov-fonts')
                    }
                }
            }
        }

        stage('Build Image') {
            environment {
                DOCKER_BUILDKIT='1'
            }
            steps {
                script {
                    docker.build(env.IMAGE_NAME_LOCAL, "--build-arg scl_python_version=rh-python36 --target cfgov-prod .")
                }
            }
        }

        stage('Scan Image') {
            steps {
                scanImage(env.IMAGE_REPO, env.IMAGE_TAG)
            }
        }

        stage('Push Image') {
            when {
                expression { return params.DEPLOY }
            } 
            steps {
                script {
                    docker.withRegistry(dockerRegistry.url, dockerRegistry.credentialsId) {
                        image = docker.image(env.IMAGE_NAME_LOCAL)
                        image.push()

                        // Sets fully-qualified image name
                        env.CFGOV_PYTHON_IMAGE = image.imageName()
                    }
                }
            }
        }

        stage('Deploy Stack') {
            when {
                expression { return params.DEPLOY }
            } 
            steps {
                script {
                    dockerStack.deploy(env.STACK_NAME, 'docker-stack.yml')
                }
                echo "Site available at: https://${CFGOV_HOSTNAME}"
            }
        }
    }
}