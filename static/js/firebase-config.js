// Firebase Client Configuration
const firebaseConfig = {
    apiKey: "AIzaSyCJNlKOrGxt19Ewv_MTH9XLb-JPlEOZMq",
    authDomain: "finsenseai-834cf.firebaseapp.com",
    projectId: "finsenseai-834cf",
    storageBucket: "finsenseai-834cf.firebasestorage.app",
    messagingSenderId: "1089787327198",
    appId: "1:1089787327198:web:a847d5d61df1444849c84f"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();
const authObj = firebase.auth();
