# Match Score Debugging Guide

## Problem
Match scores showing as 0% in the frontend, even though backend calculations are working correctly.

## Investigation Results

### Backend Tests (All Passing ✓)
1. **Model Loading**: BERT model loads correctly (384-dimension embeddings)
2. **Embedding Generation**: All 113 skills have valid embeddings
3. **Match Calculation**: Returns correct scores (100%, 65%, etc.)
4. **API View**: SkillMatchView returns proper data with match_score and match_percentage

### Test Results
```
- Model loaded: ✓
- Embeddings exist: 113/113 ✓
- Match calculation: ✓ (scores: 1.0, 0.6555)
- Direct view test: ✓ (returns 100%, 65%)
```

## Changes Made

### Frontend Improvements (3 files)

1. **`frontend/src/pages/Explore/Explore.js`**
   - Added detailed console logging to track match data flow
   - Added fallback calculation for match_percentage
   - Improved null checking for match percentage display

2. **`frontend/src/pages/Learning/Learning.js`**
   - Added detailed console logging
   - Added fallback calculation for match_percentage
   - Improved null checking

3. **`frontend/src/components/SkillMatch/SkillMatch.js`**
   - Added console logging to track API responses

## How to Debug

### Step 1: Check Browser Console
After restarting the frontend:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Search for a skill (e.g., "python")
4. Look for these logs:
   ```
   Skill matches: [...]
   First match details: {...}
   Enriched profiles: [...]
   First enriched profile: {...}
   ```

### Step 2: Verify What You See
Check the console output for:
- `match_score`: Should be a decimal (e.g., 1.0, 0.6555)
- `match_percentage`: Should be an integer (e.g., 100, 65)

### Step 3: Common Issues and Solutions

#### Issue 1: match_percentage is undefined
**Solution**: The fallback calculation now handles this:
```javascript
const matchPercentage = match.match_percentage !== undefined 
  ? match.match_percentage 
  : Math.round((match.match_score || 0) * 100);
```

#### Issue 2: match_score is very small
**Backend uses**: `int(match_score * 100)` which rounds down
**Example**: `int(0.003 * 100) = 0`
**Solution**: Use `Math.round()` instead

#### Issue 3: Data not flowing from API to display
**Check**:
1. API response in Network tab
2. Console logs for data transformation
3. Profile.data structure

## Testing Commands

### Test Backend Directly
```bash
cd backend
python debug_match_score.py
```
Should show all checks passing.

### Test API View
```bash
cd backend
python test_view_directly.py
```
Should show matches with scores > 0.

### Test Live Server
```bash
# Start Django server
cd backend
python manage.py runserver

# In another terminal, test
python test_live_api.py
```

## Expected Behavior

When searching for "python":
- Backend returns: `match_score: 1.0, match_percentage: 100`
- Frontend displays: "Match: 100%"

## Rebuild Frontend

After making these changes, rebuild the frontend:

```bash
cd frontend
npm run build
```

Or run in development mode to see live updates:
```bash
cd frontend
npm start
```

## Next Steps

1. **Restart the frontend development server** to see the console logs
2. **Check browser console** when searching for a skill
3. **Share the console output** if match scores are still 0

The logs will show exactly where the data is being lost or incorrectly transformed.
