require('dotenv').config();
const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const { google } = require('googleapis');
const { v4: uuidv4 } = require('uuid');

const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const PORT = process.env.PORT || 4000;

if (!CLIENT_ID || !CLIENT_SECRET || !REDIRECT_URI) {
  console.warn('CLIENT_ID, CLIENT_SECRET and REDIRECT_URI should be set in .env for full functionality');
}

const oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

// In-memory token store keyed by a session id cookie.
// For production use a persistent DB.
const tokenStore = {};

const app = express();
app.use(cookieParser());
app.use(express.json());
app.use(cors({ origin: FRONTEND_URL, credentials: true }));

// Provide a URL client can use to start OAuth flow
app.get('/auth/url', (req, res) => {
  if (!CLIENT_ID || !CLIENT_SECRET) {
    return res.status(500).json({ error: 'OAuth client not configured on server. Please set CLIENT_ID and CLIENT_SECRET in environment.' });
  }

  console.log('Generating auth URL with:');
  console.log('- Client ID:', CLIENT_ID.substring(0, 8) + '...');
  console.log('- Redirect URI:', REDIRECT_URI);

  const url = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: ['https://www.googleapis.com/auth/calendar.events'],
    response_type: 'code',
    redirect_uri: REDIRECT_URI,
    prompt: 'consent',
    flowName: 'GeneralOAuthFlow'
  });
  console.log('Generated auth URL (masked):', url.replace(CLIENT_ID, '[CLIENT_ID]'));
  res.json({ auth_url: url });
});

// OAuth2 callback - Google will redirect here with ?code=...
app.get('/oauth2callback', async (req, res) => {
  const code = req.query.code;
  console.log('Received OAuth callback. Code present:', !!code);
  if (!code) {
    console.error('OAuth callback error:', req.query.error);
    return res.status(400).send('Missing code');
  }

  try {
    console.log('Exchanging code for tokens...');
    const { tokens } = await oauth2Client.getToken(code);
    // Create a session id and store tokens in-memory
    const sessionId = req.cookies.sessionId || uuidv4();
    tokenStore[sessionId] = tokens;
    console.log('Tokens received and stored for session:', sessionId);
    // Set a cookie for subsequent requests
    res.cookie('sessionId', sessionId, { httpOnly: true });
    // Redirect back to frontend app
    res.redirect(FRONTEND_URL);
  } catch (err) {
    console.error('Error exchanging code for token:', err.message);
    if (err.response?.data) {
      console.error('Google API error details:', err.response.data);
    }
    res.status(500).send('Authentication failed');
  }
});

// Small endpoint to check OAuth configuration and session state
app.get('/auth/status', (req, res) => {
  const configured = !!(CLIENT_ID && CLIENT_SECRET && REDIRECT_URI);
  const sessionId = req.cookies.sessionId;
  const hasSession = !!(sessionId && tokenStore[sessionId]);
  res.json({ 
    configured,
    hasSession,
    clientIdPresent: !!CLIENT_ID,
    redirectUri: REDIRECT_URI 
  });
});

// Create a Google Meet (via Calendar API event with conferenceData.createRequest)
app.post('/api/create-meet', async (req, res) => {
  if (!CLIENT_ID || !CLIENT_SECRET) {
    return res.status(500).json({ error: 'OAuth client not configured on server. Please set CLIENT_ID and CLIENT_SECRET in environment.' });
  }
  const sessionId = req.cookies.sessionId;
  if (!sessionId || !tokenStore[sessionId]) {
    // Not authenticated: return an auth URL so frontend can redirect user
    const url = oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: ['https://www.googleapis.com/auth/calendar.events'],
      prompt: 'consent'
    });
    return res.status(401).json({ auth_url: url });
  }

  const tokens = tokenStore[sessionId];
  oauth2Client.setCredentials(tokens);
  const calendar = google.calendar({ version: 'v3', auth: oauth2Client });

  // Accept optional summary/description from frontend
  const { summary = 'Chat meeting', description = 'Meeting created from chat app' } = req.body || {};

  const startDate = new Date(Date.now() + 5 * 60 * 1000).toISOString(); // start in 5 minutes
  const endDate = new Date(Date.now() + 35 * 60 * 1000).toISOString(); // 30-minute meeting

  const event = {
    summary,
    description,
    start: { dateTime: startDate },
    end: { dateTime: endDate },
    conferenceData: {
      createRequest: {
        requestId: uuidv4()
      }
    }
  };

  try {
    console.log('Creating calendar event with Meet...');
    const response = await calendar.events.insert({
      calendarId: 'primary',
      resource: event,
      conferenceDataVersion: 1
    });

    const created = response.data;
    console.log('Event created:', created.id);
    // extract join link (hangoutLink or conferenceData entryPoints)
    const meetLink = created.hangoutLink || (created.conferenceData && created.conferenceData.entryPoints && created.conferenceData.entryPoints.find(ep => ep.entryPointType === 'video')?.uri) || null;
    console.log('Meet link generated:', !!meetLink);

    return res.json({ meetLink, event: created });
  } catch (err) {
    console.error('Failed to create calendar event:', err.message);
    if (err.response?.data) {
      console.error('Google API error details:', err.response.data);
    }
    return res.status(500).json({ error: 'Failed to create meeting', details: err.message });
  }
});

app.get('/', (req, res) => res.send('Google Meet backend running'));

app.listen(PORT, () => console.log(`Google Meet backend listening on http://localhost:${PORT}`));