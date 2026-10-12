import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Details } from './details/details';

// startseite mit der liste, details seite mit der id aus der url
export const routes: Routes = [
  {
    path: '',
    component: Home,
    title: 'Home page',
  },
  {
    path: 'details/:id',
    component: Details,
    title: 'Home details',
  },
];
