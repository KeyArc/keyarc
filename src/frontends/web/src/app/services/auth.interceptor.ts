import { HttpInterceptorFn } from '@angular/common/http';

/**
 * HTTP Interceptor for adding authentication headers to requests.
 *
 * This is a functional interceptor (Angular 17+ pattern) that will be expanded
 * to add JWT tokens from the auth service once authentication is implemented.
 *
 * Current implementation: Pass-through stub
 * Future implementation: Add Authorization header with JWT token
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // TODO: Implement JWT token injection
  // const token = inject(AuthService).getToken();
  // if (token) {
  //   req = req.clone({
  //     setHeaders: {
  //       Authorization: `Bearer ${token}`
  //     }
  //   });
  // }

  return next(req);
};
