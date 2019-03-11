pipeline {
    agent none
    environment {
        DOCKER_REPO = "boerderij/varken"
        GIT_REPO = 'Boerderij/Varken'
        VERSION_FILE = "varken/__init__.py"
        FLAKE_FILES = "Varken.py varken/*.py"
        TAG = ""
        GIT_TOKEN = credentials('github-jenkins-token')
    }
    stages {
        stage('Flake8') {
            agent { label 'amd64'}
            steps {
                sh """
                    python3 -m venv venv && venv/bin/pip install flake8 && venv/bin/python -m flake8 --max-line-length 120 ${FLAKE_FILES}
                    rm -rf venv/
                """
                script {
                    TAG = sh(returnStdout: true, script: 'grep -i version ${VERSION_FILE} | cut -d" " -f3 | tr -d \\"').trim()
                }
            }
        }
        stage('Docker Builds') {
            parallel {
                stage('amd64') {
                    when {
                        anyOf {
                            branch 'master'
                            branch 'develop'
                        }
                    }
                    agent { label 'amd64'}
                    steps {
                        script {
                            if (BRANCH_NAME == 'master') {
                                def image = docker.build("${DOCKER_REPO}:${TAG}-amd64")
                                image.push()
                                
                            } else if (BRANCH_NAME == 'develop') {
                                def image = docker.build("${DOCKER_REPO}:develop-amd64")
                                image.push()
                            }
                        }
                    }
                }
                stage('ARMv6') {
                    when {
                        anyOf {
                            branch 'master'
                            branch 'develop'
                        }
                    }
                    agent { label 'arm64'}
                    steps {
                        script {
                            if (BRANCH_NAME == 'master') {
                                def image = docker.build("${DOCKER_REPO}:${TAG}-arm", "-f Dockerfile.arm .")
                                image.push()
                            } else if (BRANCH_NAME == 'develop') {
                                def image = docker.build("${DOCKER_REPO}:develop-arm", "-f Dockerfile.arm .")
                                image.push()
                            }
                        }
                    }
                }
                stage('ARM64v8') {
                    when {
                        anyOf {
                            branch 'master'
                            branch 'develop'
                        }
                    }
                    agent { label 'arm64'}
                    steps {
                        script {
                            if (BRANCH_NAME == 'master') {
                                def image = docker.build("${DOCKER_REPO}:${TAG}-arm64", "-f Dockerfile.arm64 .")
                                image.push()
                            } else if (BRANCH_NAME == 'develop') {
                                def image = docker.build("${DOCKER_REPO}:develop-arm64", "-f Dockerfile.arm64 .")
                                image.push()
                            }
                        }
                    }
                }
            }
        }
        stage('Docker Manifest Build') {
            when {
                anyOf {
                    branch 'master'
                    branch 'develop'
                }
            }
            agent { label 'amd64'}
            steps {
                script {
                    if (BRANCH_NAME == 'master') {
                        sh(script: "docker manifest create ${DOCKER_REPO}:${TAG} ${DOCKER_REPO}:${TAG}-amd64 ${DOCKER_REPO}:${TAG}-arm64 ${DOCKER_REPO}:${TAG}-arm")
                        sh(script: "docker manifest inspect ${DOCKER_REPO}:${TAG}")
                        sh(script: "docker manifest push -p ${DOCKER_REPO}:${TAG}")
                        sh(script: "docker manifest create ${DOCKER_REPO}:latest ${DOCKER_REPO}:${TAG}-amd64 ${DOCKER_REPO}:${TAG}-arm64 ${DOCKER_REPO}:${TAG}-arm")
                        sh(script: "docker manifest inspect ${DOCKER_REPO}:latest")
                        sh(script: "docker manifest push -p ${DOCKER_REPO}:latest")
                    } else if (BRANCH_NAME == 'develop') {
                        sh(script: "docker manifest create ${DOCKER_REPO}:develop ${DOCKER_REPO}:develop-amd64 ${DOCKER_REPO}:develop-arm64 ${DOCKER_REPO}:develop-arm")
                        sh(script: "docker manifest inspect ${DOCKER_REPO}:develop")
                        sh(script: "docker manifest push -p ${DOCKER_REPO}:develop")
                    }
                }
            }
        }
        stage('GitHub Release') {
            when { branch 'master' }
            agent { label 'amd64'}
            steps {
                sh """
                    git remote set-url origin "https://${GIT_TOKEN_USR}:${GIT_TOKEN_PSW}@github.com/${GIT_REPO}.git" 
                    git tag ${TAG}
                    git push --tags
                """
            }
        }
    }
}
