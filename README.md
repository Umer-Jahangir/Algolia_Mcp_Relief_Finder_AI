# Relief Finder AI – Powered by Algolia MCP

Relief Finder AI is a full-stack, AI-powered disaster response application that helps users quickly locate relief shelters, resources, disaster alerts, and safety information during emergencies. Built with React, Django, Algolia, and OpenRouter AI, it integrates real-time disaster alerts, geolocation, weather APIs, and intelligent search to provide life-saving information through a smart and responsive interface.

## Features

### Smart Search with Algolia
- Find relief shelters by filtering food, water, medical aid, accessibility, etc.

- Search shelters near your current location using geolocation.

### AI Chat Assistant
- Ask natural-language questions like:

  - “Is there any shelter with food and water nearby?”

  - “Any flood alerts in Punjab?”

- AI automatically chooses the right Algolia index (e.g., Relief Shelters  or disaster alerts) and returns contextual answers.

Powered by OpenRouter AI (e.g. AI Model) with custom prompt engineering.

### Real-Time Disaster Alerts
- Alerts fetched from the disaster_alerts index in Algolia.

- Categorized by type (e.g., floods, earthquakes, storms).

- Alerts are location-aware and shown on the map.

### Interactive Map View
- Map powered by Leaflet.

- Displays relief shelters and disaster zones with markers.

- Route suggestions between user and shelters.

### Live Weather Information
- Uses OpenWeatherMap API.

- Shows current weather at both the user’s location and each shelter site.

- Useful for planning safe movement and shelter conditions.

### Full Stack Integration
- Frontend: React + TailwindCSS + Lucide icons

- Backend: Django + DRF + Algolia MCP + AI (via OpenRouter)

- Secure .env support for API keys and credentials


## Tech Stack  

| Frontend     | Backend | AI & Search         | Others         |
| ------------ | ------- | ------------------- | -------------- |
| React.js     | Django  | Algolia MCP         | Leaflet Maps   |
| Tailwind     | DRF     | OpenRouter          | OpenWeatherMap |
| Lucide Icons | Python  | AI Model            | .env Config    |


##  AI Integration Workflow
```bash
graph TD
A[User enters query] --> B[React sends to Django AI endpoint]
B --> C[Start Algolia Mcp server from Backend [cli]]
C --> D[Determine Algolia index via AI]
D --> E[Use MCP Tool: searchSingleIndex]
E --> F[Fetch enriched data from Algolia index]
F --> G[Generate AI response with AI Model]
G --> H[Return contextual response to React frontend]
```

## Setup Instructions
1. Clone Repository
   ```bash
   https://github.com/Umer-Jahangir/Algolia_Mcp_Relief_Finder_AI.git
   cd Algolia_Mcp_Relief_Finder_AI
   ```
2. Frontend Setup
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Add VITE_OPENWEATHERMAP_KEY and ALGOLIA credentials
   npm run dev
   ```
3. Backend Setup (Django)
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Add Algolia, OpenRouter keys
   python manage.py runserver
   ```
4. Set up the Algolia MCP Server
   
   This project requires a running instance of the <a href="[https://github.com/algolia/mcp](https://github.com/algolia/mcp-node)" target="_blank">Algolia MCP Server</a>. This server acts as a secure proxy that executes commands for the Algolia API.
   - If you don't have it, clone the official repository
     ```bash
     git clone https://github.com/algolia/mcp-node.git
     ```
     It is recommended to clone it into a separate directory from this project (e.g., `C:/dev/mcp-node` or `~/dev/mcp-node`).
   - Navigate to the MCP server directory
     ```bash
     cd path/to/your/mcp-node
     ```
   - Install Node.js dependencies
     ```bash
     npm install
     ```
   - Ensure the path to this directory is set in the `MCP_NODE_PATH` variable in our project's `.env` file.
   - Note : It is a Command Line Interface may not run local server only perform actions and you confirm it after `npm start` and get `algolia start` message in via `cli`. 
     
## Environment Variables
Frontend `.env`
```bash
VITE_OPENWEATHERMAP_KEY=your_key
VITE_ALGOLIA_APP_ID=your_app_id
VITE_ALGOLIA_SEARCH_KEY=your_search_key
```
Backend `.env`
```bash
ALGOLIA_APP_ID=your_id
ALGOLIA_API_KEY=your_admin_key
OPENROUTER_API_KEY=your_openrouter_key
```

##  Project Structure
```bash
Algolia_Mcp_Relief_Finder_AI/
├── backend/
│   ├── chat_assistant/  # Handles AI chat logic (MCP, OpenRouter)
│   ├──  Distarers/      # Handles disaster data ingestion and indexing to my Algolia (You can manage by your index)
│   ├──  relief_shelter/ # Handles Relief shelters data ingestion and indexing to my Algolia (You can manage by your index)
│   └── ...
├── frontend/
│   └──  src/
│        ├── components/ # React UI components main files on App Interface (Dashboard, AI Chat, etc.)
│   ├── App.jsx
│   └── main.jsx
├── public/
├── .env.example         # Contains env variables (Algolia, weather, etc.)
├── README.md

```
##  Credits
- Algolia

- OpenRouter

- OpenWeatherMap

- LeafletJS

## License

MIT License. Feel free to fork and enhance this project for your own region or use case.






