After Extracting ZIP:

Create .env file:
env
MONGODB_URL=mongodb+srv://...
GROK_API_KEY=your_api_key_here
SECRET_KEY=your_jwt_secret

Install dependencies:
bash
cd backend
pip install -r requirements.txt
 
cd ../frontend
npm install

Start the application:
bash
#Terminal 1: Backend
cd backend
python main_new.py
 
#Terminal 2: Frontend
cd frontend
npm start

Access the application:
http://127.0.0.1:5500/frontend/index.html
