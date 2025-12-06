# FinSense AI

FinSense is a gamified financial literacy web application for youth, built with Flask and Vanilla JS.

## Prerequisites

- Python 3.8+
- Git

## How to Run Locally

1.  **Clone or Navigate to the directory:**
    ```bash
    cd d:\Project_2k24_25\fin-sence\FinSenseAI
    ```

2.  **Install Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    # Create virtual environment
    python -m venv venv

    # Activate virtual environment
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    # source venv/bin/activate

    # Install Flask (if not already installed)
    pip install flask
    ```

3.  **Run the Application:**
    ```bash
    python app.py
    ```

4.  **Access the App:**
    Open your web browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## How to Push to Git

1.  **Initialize Git (if not already done):**
    ```bash
    git init
    ```

2.  **Add Files:**
    ```bash
    git add .
    ```

3.  **Commit Changes:**
    ```bash
    git commit -m "Initial commit: FinSense UI with Flask backend"
    ```

4.  **Add Remote Repository:**
    Replace `<your-repo-url>` with your actual GitHub/GitLab repository URL.
    ```bash
    git remote add origin <your-repo-url>
    ```

5.  **Push Code:**
    ```bash
    git branch -M main
    git push -u origin main
    ```

## Project Structure

- `app.py`: Flask backend application.
- `templates/`: HTML templates (Jinja2).
- `static/`: CSS, JavaScript, and images.
