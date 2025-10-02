import api from './geoApi.js';

export const mapService = {
  cities: () => 
    api.get('/cities.geojson').then(r => r.data),

  russia: () => 
    api.get('/russia.geojson').then(r => r.data),

  routes: () => 
    api.get('/routes.json').then(r => r.data),
};
