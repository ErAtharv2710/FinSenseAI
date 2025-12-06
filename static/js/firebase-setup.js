// Firebase Setup
fetch('/api/config/firebase')
    .then(res => res.json())
    .then(config => {
        if (config.apiKey) {
            firebase.initializeApp(config);
            console.log('Firebase Initialized');
        }
    });
