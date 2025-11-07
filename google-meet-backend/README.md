Google Meet backend (local testing)

This small Express app helps create Google Meet links via the Google Calendar API using OAuth2.

Setup
1. Copy `.env.example` to `.env` and set CLIENT_ID, CLIENT_SECRET, REDIRECT_URI and FRONTEND_URL.
2. Install dependencies:

   npm install

3. Start the server:

   npm start

Endpoints
- GET /auth/url -> returns a JSON with auth_url to start OAuth flow
- GET /oauth2callback -> Google will call this endpoint with ?code=...; the server exchanges the code for tokens and stores them in-memory (in cookie session)
- POST /api/create-meet -> creates a calendar event with conferenceData and returns the Meet link.

Notes
- This is a demo/local-testing implementation. Tokens are stored in-memory (not safe for production). Use a DB in production.
- Make sure the Google OAuth client has the redirect URI configured exactly as REDIRECT_URI.
- CORS is enabled for FRONTEND_URL.
