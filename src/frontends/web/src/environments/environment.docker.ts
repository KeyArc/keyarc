/**
 * Docker environment configuration
 * Used with: ng build --configuration=docker
 * For local containerized development
 */
export const environment = {
  production: false,
  envName: 'docker',
  apiUrl: 'http://localhost:8080/api',
  authUrl: 'http://localhost:8080/auth'
};
