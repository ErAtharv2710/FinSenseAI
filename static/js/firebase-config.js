// Firebase Config Fetcher
fetch('/api/config/firebase')
    .then(response => response.json())
    .then(config => {
        if (config.apiKey && config.apiKey !== 'None') {
            firebase.initializeApp(config);
            console.log('Firebase initialized');
        } else {
            console.warn('Firebase config missing or incomplete.');
        }
    })
    .catch(err => console.error('Error loading Firebase config:', err));
