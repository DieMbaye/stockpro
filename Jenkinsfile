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

        stage('Déploiement (staging)') {
            steps {
                withCredentials([string(credentialsId: 'stockpro-staging-db-password', variable: 'POSTGRES_PASSWORD')]) {
                    sh 'docker compose -f deploy/docker-compose.staging.yml up -d --pull always'
                }
            }
        }

        stage('Vérification de santé') {
            steps {
                withCredentials([string(credentialsId: 'stockpro-staging-db-password', variable: 'POSTGRES_PASSWORD')]) {
                    sh '''
                        echo "Vérification de StockPro staging..."
                        for i in $(seq 1 30); do
                          if curl -fsS http://host.docker.internal:8091/api/health; then
                            echo ""
                            echo "✅ StockPro staging est en bonne santé (version $IMAGE_TAG)"
                            exit 0
                          fi
                          sleep 3
                        done
                        echo "❌ L'application ne répond pas : voici ses derniers logs"
                        docker compose -f deploy/docker-compose.staging.yml logs --tail=50
                        exit 1
                    '''
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
            echo "✅ Version ${IMAGE_TAG} testée, publiée et déployée en staging !"
        }
        failure {
            echo '❌ Pipeline en échec : regarde l\'étape en rouge pour comprendre pourquoi.'
        }
    }
}