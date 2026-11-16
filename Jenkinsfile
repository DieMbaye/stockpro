pipeline {
    agent any

    environment {
        RESEAU_CI = "stockpro-ci-${BUILD_NUMBER}"
        DB_CI     = "stockpro-db-ci-${BUILD_NUMBER}"
        // Mot de passe jetable : la base de test n'existe que pendant le build,
        // dans un réseau privé, sans aucun port ouvert vers l'extérieur.
        DB_CI_PASSWORD = "ci_jetable"
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
                    docker build -t stockpro-backend:$BUILD_NUMBER backend
                    docker build -t stockpro-frontend:$BUILD_NUMBER frontend
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f "$DB_CI" || true
                docker network rm "$RESEAU_CI" || true
                docker rmi stockpro-backend-test:$BUILD_NUMBER || true
            '''
        }
        success {
            echo '✅ Pipeline réussi : tests OK et images construites !'
        }
        failure {
            echo '❌ Pipeline en échec : regarde l\'étape en rouge pour comprendre pourquoi.'
        }
    }
}