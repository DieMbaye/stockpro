pipeline {
    agent any

    environment {
        RESEAU_CI = "stockpro-ci-${BUILD_NUMBER}"
        DB_CI     = "stockpro-db-ci-${BUILD_NUMBER}"
        // Mot de passe jetable : la base de test n'existe que pendant le build,
        // dans un réseau privé, sans aucun port ouvert vers l'extérieur.
        DB_CI_PASSWORD = "ci_jetable"

        IMAGE_BACKEND  = "diemb/stockpro-backend"
        IMAGE_FRONTEND = "diemb/stockpro-frontend"
        IMAGE_TAG      = "${GIT_COMMIT.take(7)}"
    }

    stages {
        stage('Vérifier le déclencheur') {
            steps {
                script {
                    def message = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                    if (message.contains('[skip ci]')) {
                        env.IGNORER = 'true'
                        currentBuild.result = 'NOT_BUILT'
                        currentBuild.description = 'Commit GitOps de Jenkins : ignoré'
                        echo "⏭️ Commit marqué [skip ci] : aucune étape ne sera lancée."
                    } else {
                        env.IGNORER = 'false'
                    }
                }
            }
        }

        stage('CI/CD') {
            when {
                expression { env.IGNORER != 'true' }
            }
            stages {
                stage('Recherche de secrets (Gitleaks)') {
                    steps {
                        sh '''
                            docker run --rm -u 0 \
                              --volumes-from jenkins \
                              -w "$WORKSPACE" \
                              ghcr.io/gitleaks/gitleaks:latest \
                              git --redact -v --exit-code 1 .
                        '''
                    }
                }

                stage('Préparer la base de test') {
                    steps {
                        sh '''
                            docker network create "$RESEAU_CI"
                            docker run -d --name "$DB_CI" --network "$RESEAU_CI" \
                              -e POSTGRES_USER=stockpro \
                              -e POSTGRES_PASSWORD="$DB_CI_PASSWORD" \
                              -e POSTGRES_DB=stockpro_test \
                              postgres:17-alpine

                            echo "Attente de PostgreSQL..."
                            for i in $(seq 1 30); do
                              if docker exec "$DB_CI" pg_isready -h localhost -U stockpro; then
                                exit 0
                              fi
                              sleep 2
                            done
                            echo "PostgreSQL n'a pas démarré à temps"
                            exit 1
                        '''
                    }
                }

                stage('Tests du backend') {
                    steps {
                        sh '''
                            docker build -f backend/Dockerfile.test -t stockpro-backend-test:$BUILD_NUMBER backend
                            docker run --rm --network "$RESEAU_CI" \
                              -e TEST_DATABASE_URL="postgresql+psycopg://stockpro:$DB_CI_PASSWORD@$DB_CI:5432/stockpro_test" \
                              stockpro-backend-test:$BUILD_NUMBER
                        '''
                    }
                }

                stage('Construction des images') {
                    steps {
                        sh '''
                            docker build -t "$IMAGE_BACKEND:$IMAGE_TAG" -t "$IMAGE_BACKEND:latest" backend
                            docker build -t "$IMAGE_FRONTEND:$IMAGE_TAG" -t "$IMAGE_FRONTEND:latest" frontend
                        '''
                    }
                }

                stage('Publication sur Docker Hub') {
                    steps {
                        withCredentials([usernamePassword(
                            credentialsId: 'dockerhub',
                            usernameVariable: 'DOCKERHUB_USER',
                            passwordVariable: 'DOCKERHUB_TOKEN'
                        )]) {
                            sh '''
                                echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
                                docker push "$IMAGE_BACKEND:$IMAGE_TAG"
                                docker push "$IMAGE_BACKEND:latest"
                                docker push "$IMAGE_FRONTEND:$IMAGE_TAG"
                                docker push "$IMAGE_FRONTEND:latest"
                            '''
                        }
                    }
                }

                stage('Mise à jour GitOps') {
                    steps {
                        withCredentials([usernamePassword(
                            credentialsId: 'github-token',
                            usernameVariable: 'GITHUB_USER',
                            passwordVariable: 'GITHUB_TOKEN'
                        )]) {
                            sh '''
                                sed -i "s|image: diemb/stockpro-backend:.*|image: diemb/stockpro-backend:$IMAGE_TAG|" k8s/backend.yaml
                                sed -i "s|image: diemb/stockpro-frontend:.*|image: diemb/stockpro-frontend:$IMAGE_TAG|" k8s/frontend.yaml

                                git config user.name "Jenkins CI"
                                git config user.email "jenkins@stockpro.local"
                                git add k8s/backend.yaml k8s/frontend.yaml

                                if git diff --cached --quiet; then
                                  echo "Les manifestes sont déjà à jour"
                                  exit 0
                                fi

                                git commit -m "GitOps : déploiement des images $IMAGE_TAG [skip ci]"
                                git push "https://$GITHUB_USER:$GITHUB_TOKEN@github.com/DieMbaye/stockpro.git" HEAD:main
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker logout || true
                docker rm -f "$DB_CI" || true
                docker network rm "$RESEAU_CI" || true
                docker rmi stockpro-backend-test:$BUILD_NUMBER || true
            '''
        }
        success {
            echo "✅ Version ${IMAGE_TAG} testée et publiée. Argo CD va la déployer dans Kubernetes 🐙"
        }
        notBuilt {
            echo "⏭️ Build ignoré (commit [skip ci])."
        }
        failure {
            echo '❌ Pipeline en échec : regarde l\'étape en rouge pour comprendre pourquoi.'
        }
    }
}