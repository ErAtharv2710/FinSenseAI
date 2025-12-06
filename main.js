// main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pythonProcess = null;
let mainWindow = null;

// --- 1. PYTHON PROCESS MANAGEMENT ---

function startPythonBackend() {
    const scriptPath = path.join(__dirname, 'backend', 'app.py');

    // Launch the Python Flask server
    // Note: Use 'python' if your venv is activated, or the full path to python.exe
    pythonProcess = spawn('python', [scriptPath]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python Output]: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        // Essential for debugging Flask/Python errors!
        console.error(`[Python Error]: ${data}`);
    });

    console.log('Python Flask Server spawned on port 5000...');

    // Give the server a moment to start before creating the window
    setTimeout(createWindow, 2000);
}

function killPythonBackend() {
    if (pythonProcess) {
        // Sends a kill signal to the process
        pythonProcess.kill();
        console.log('Python Flask Server killed.');
    }
}

// --- 2. ELECTRON WINDOW MANAGEMENT ---

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            // REMOVED: preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: false // Simplifies development/POC
        }
    });

    mainWindow.loadFile('index.html');
}

// --- 3. APP LIFECYCLE ---

app.whenReady().then(() => {
    startPythonBackend(); // Start the server first
});

// Quit when all windows are closed, and kill the Python server
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('will-quit', killPythonBackend);

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});