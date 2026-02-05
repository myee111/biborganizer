# Enable Anthropic Models on Vertex AI

The 404 error you're seeing means that Anthropic's Claude models are not yet enabled or accessible in your Google Cloud project. Follow this guide to enable them.

## Error You're Seeing

```
Error code: 404 - Publisher Model was not found or your project does not have access to it.
```

## Step 1: Enable Vertex AI API

```bash
# Enable the Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=itpc-gcp-product-all-claude

# Verify it's enabled
gcloud services list --enabled --project=itpc-gcp-product-all-claude | grep aiplatform
```

## Step 2: Request Access to Anthropic Models (If Needed)

Anthropic models on Vertex AI may require special access or allowlisting:

### Option A: Through GCP Console

1. Go to [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. Search for "Claude" or "Anthropic"
3. Click on a Claude model (e.g., Claude 3.5 Sonnet)
4. Click "Enable" or "Request Access" if prompted
5. Follow any additional steps to grant access

### Option B: Through Support

If models aren't visible in Model Garden:

1. Contact Google Cloud Support
2. Request access to "Anthropic Claude models on Vertex AI"
3. Provide your project ID: `itpc-gcp-product-all-claude`

## Step 3: Check IAM Permissions

Ensure your account has the necessary permissions:

```bash
# Check your current permissions
gcloud projects get-iam-policy itpc-gcp-product-all-claude \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"
```

You need one of these roles:
- `roles/aiplatform.user`
- `roles/aiplatform.admin`
- `roles/owner`

To add the role:
```bash
gcloud projects add-iam-policy-binding itpc-gcp-product-all-claude \
  --member="user:YOUR_EMAIL" \
  --role="roles/aiplatform.user"
```

## Step 4: Check Model Availability by Region

Anthropic models may not be available in all regions. Try different regions:

### Test us-central1

Edit `.env`:
```bash
VERTEX_REGION=us-central1
```

Then test:
```bash
source venv/bin/activate
python test_vertex_connection.py
```

### Test europe-west1

Edit `.env`:
```bash
VERTEX_REGION=europe-west1
```

Then test again.

### Available Regions for Anthropic Models

Check the latest list:
https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude

Common regions:
- `us-east5`
- `us-central1`
- `europe-west1`
- `asia-southeast1`

## Step 5: Verify Authentication

Make sure you're authenticated:

```bash
# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project itpc-gcp-product-all-claude

# Verify
gcloud auth application-default print-access-token
```

## Step 6: Check Billing

Anthropic models on Vertex AI require billing to be enabled:

1. Go to [GCP Billing](https://console.cloud.google.com/billing)
2. Verify project `itpc-gcp-product-all-claude` has a billing account linked
3. Enable billing if not already enabled

## Alternative: Use Anthropic API Directly

If Vertex AI setup is taking too long, you can use the direct Anthropic API instead:

### Switch to Anthropic API

1. Get an API key from https://console.anthropic.com

2. Edit `.env`:
```bash
USE_VERTEX_AI=false
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
CLAUDE_MODEL=sonnet-4.5
```

3. Test:
```bash
source venv/bin/activate
python test_installation.py
```

This will let you start using the photo organizer immediately while you work on Vertex AI access.

## Troubleshooting Commands

### List all enabled services
```bash
gcloud services list --enabled --project=itpc-gcp-product-all-claude
```

### Check project info
```bash
gcloud projects describe itpc-gcp-product-all-claude
```

### Test Vertex AI access
```bash
gcloud ai models list --region=us-east5 --project=itpc-gcp-product-all-claude
```

### Check available Claude models (if API is enabled)
```bash
# This command might not work if models aren't enabled yet
gcloud ai models list \
  --region=us-east5 \
  --project=itpc-gcp-product-all-claude \
  --filter="displayName:claude"
```

## Getting Help

### GCP Support
- [Vertex AI Support](https://cloud.google.com/vertex-ai/docs/support/getting-support)
- Submit a support ticket through GCP Console

### Check Status
- [GCP Status Dashboard](https://status.cloud.google.com/)
- [Anthropic Status](https://status.anthropic.com/)

### Documentation
- [Anthropic on Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude)
- [Vertex AI Quotas](https://cloud.google.com/vertex-ai/docs/quotas)

## Expected Timeline

- **API Enablement:** Immediate
- **IAM Permission Changes:** Immediate
- **Model Access Request:** 1-2 business days
- **Region Availability:** Check documentation

## Quick Test After Enabling

Once you've completed the setup, run:

```bash
source venv/bin/activate
python test_vertex_connection.py
```

You should see:
```
✓ Using Vertex AI model format
✓ Client initialized successfully
✓ API Response: Hello! API connection successful.
✓ Connection test PASSED!
```

## Need Immediate Access?

While waiting for Vertex AI access, use Anthropic API:

1. Sign up at https://console.anthropic.com
2. Get API key
3. Update `.env`:
   ```bash
   USE_VERTEX_AI=false
   ANTHROPIC_API_KEY=your_key_here
   ```
4. Start organizing photos immediately!

You can always switch back to Vertex AI later.
