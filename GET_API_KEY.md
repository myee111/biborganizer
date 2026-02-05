# Get Your Anthropic API Key

## Quick Steps

1. **Go to Anthropic Console:**
   - Visit: https://console.anthropic.com

2. **Sign Up / Log In:**
   - Create an account or log in with Google/GitHub
   - You may need to verify your email

3. **Get Your API Key:**
   - Click "Get API Keys" or go to Settings
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-api03-...`)
   - **Important:** Save it somewhere - you won't see it again!

4. **Add Credits (if needed):**
   - New accounts get $5 free credit
   - Add payment method for more: Settings → Billing
   - Typical usage: $1-2 per 100 photos

5. **Update Your .env File:**
   ```bash
   nano .env
   ```

   Replace this line:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

   With your actual key:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-xxx...
   ```

6. **Test It:**
   ```bash
   source venv/bin/activate
   python test_installation.py
   ```

## You're Done!

Once you see all checkmarks, you can start organizing photos:
```bash
python manage_database.py
```

## Pricing

- Free tier: $5 credit (good for ~250-500 photos)
- Pay-as-you-go: ~$0.01-0.02 per photo
- 1000 photos: ~$10-20

Much cheaper than manually organizing photos!
