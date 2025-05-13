# Travelo Backend

A powerful backend service for the Travelo travel planning application, providing AI-powered trip planning, weather information, and various travel-related APIs.

## Features

- 🤖 AI-powered trip planning with detailed itineraries
- 🌤️ Real-time weather information
- 🗺️ Google Maps integration
- 🔐 Secure API key management
- 🌐 Multi-language support
- 💱 Multi-currency support

## Tech Stack

- Node.js
- Express.js
- OpenAI API
- Google Maps API
- OpenWeather API
- Railway.app (Deployment)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yusaislam48/travelo-backend.git
cd travelo-backend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory with the following variables:
```env
PORT=3000
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

4. Start the development server:
```bash
npm run dev
```

## API Endpoints

### Trip Planning

#### POST /api/plan-trip
Generate a detailed trip plan using AI.

**Request Body:**
```json
{
  "origin": "Dhaka",
  "destination": "New York",
  "date": "2024-03-20",
  "language": "en",
  "currency": "USD"
}
```

**Response:**
```json
{
  "result": "Markdown formatted trip plan"
}
```

### Configuration

#### GET /api/config/maps-key
Get the Google Maps API key.

**Response:**
```json
{
  "key": "your_google_maps_api_key"
}
```

#### GET /api/config/weather-key
Get the OpenWeather API key.

**Response:**
```json
{
  "key": "your_openweather_api_key"
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| PORT | Server port number |
| OPENAI_API_KEY | OpenAI API key for AI trip planning |
| GOOGLE_MAPS_API_KEY | Google Maps API key for location services |
| OPENWEATHER_API_KEY | OpenWeather API key for weather data |

## Deployment

The backend is deployed on Railway.app. The production URL is:
```
https://travelo-backend-production-454e.up.railway.app
```

## Security

- API keys are stored securely and not exposed to the frontend
- All API endpoints are protected with appropriate rate limiting
- Environment variables are used for sensitive data

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - your.email@example.com
Project Link: https://github.com/yourusername/travelo-backend
