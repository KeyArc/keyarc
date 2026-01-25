import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./components/layout/layout.component').then(m => m.LayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      // Placeholder routes for future features
      // {
      //   path: 'secrets',
      //   loadComponent: () =>
      //     import('./components/secrets/secrets.component').then(m => m.SecretsComponent)
      // },
      // {
      //   path: 'teams',
      //   loadComponent: () =>
      //     import('./components/teams/teams.component').then(m => m.TeamsComponent)
      // },
      // {
      //   path: 'settings',
      //   loadComponent: () =>
      //     import('./components/settings/settings.component').then(m => m.SettingsComponent)
      // }
    ]
  },
  // Auth routes (outside main layout)
  // {
  //   path: 'auth',
  //   children: [
  //     {
  //       path: 'login',
  //       loadComponent: () =>
  //         import('./components/auth/login/login.component').then(m => m.LoginComponent)
  //     },
  //     {
  //       path: 'signup',
  //       loadComponent: () =>
  //         import('./components/auth/signup/signup.component').then(m => m.SignupComponent)
  //     }
  //   ]
  // },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
