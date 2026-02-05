# Enable Anthropic Models on Vertex AI - Do This Now

## The Issue

Your GCP project `itpc-gcp-product-all-claude` has Vertex AI enabled, but **Anthropic's Claude models are not enabled yet**. You need to enable them through the GCP Console.

## Step-by-Step Instructions

### 1. Open Vertex AI Model Garden

**Go to:** https://console.cloud.google.com/vertex-ai/model-garden

**Make sure** you're in the right project: `itpc-gcp-product-all-claude`
(Check the project dropdown at the top of the page)

### 2. Find Claude Models

In the Model Garden search box, type: **"Claude"**

You should see models like:
- Claude 3.5 Sonnet
- Claude 3.5 Haiku
- Claude 3 Opus

### 3. Enable a Model

1. Click on **"Claude 3.5 Sonnet"** (recommended)
2. You'll see a model details page
3. Look for one of these buttons:
   - **"Enable"** - Click it!
   - **"Request Access"** - Click it and fill out the form
   - **"Get Started"** or **"Use Model"** - Click it
4. If there's a Terms of Service, accept it
5. If prompted to select a region, choose **us-central1**

### 4. Wait for Enablement

- **If you clicked "Enable":** Usually instant to a few minutes
- **If you submitted "Request Access":** May take 1-2 business days

### 5. Test It

Once enabled, come back and run:

```bash
source venv/bin/activate
python test_vertex_connection.py
```

You should see:
```
✓ Connection test PASSED!
```

## Alternative: Enable via Command (if you have permission)

If you're a project owner/admin, try this:

```bash
# This might work if you have the right permissions
gcloud services enable aiplatform.googleapis.com --project=itpc-gcp-product-all-claude
```

## Troubleshooting

### "I don't see Claude models in Model Garden"

**Possible reasons:**
1. Anthropic models not available in your region yet
2. Your organization has restrictions
3. Billing not enabled

**Try:**
- Check you're in the right project
- Ensure billing is enabled: https://console.cloud.google.com/billing
- Try a different region (us-central1, europe-west1)

### "I don't have permission"

You need one of these roles:
- `roles/aiplatform.admin`
- `roles/owner`
- `roles/editor`

**Ask your GCP admin to:**
1. Go to IAM & Admin: https://console.cloud.google.com/iam-admin/iam
2. Find your email: myee@redhat.com
3. Add role: **Vertex AI User** or **Vertex AI Administrator**

Or ask them to enable Anthropic models for the project.

### "Request Access" form - what to put?

- **Use case:** "Photo organization using facial recognition"
- **Expected usage:** "Processing personal photo library"
- **Region preference:** us-central1

## Current Status

- ✅ Vertex AI API enabled
- ✅ Project ID configured: itpc-gcp-product-all-claude
- ✅ Region set: us-central1
- ❌ Anthropic models NOT enabled yet ← **You need to fix this**

## Links

- Model Garden: https://console.cloud.google.com/vertex-ai/model-garden
- Project IAM: https://console.cloud.google.com/iam-admin/iam?project=itpc-gcp-product-all-claude
- Billing: https://console.cloud.google.com/billing
- Anthropic on Vertex AI Docs: https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude

## Once Enabled

After Anthropic models are enabled, you can:

```bash
# Test connection
source venv/bin/activate
python test_vertex_connection.py

# Add people
python manage_database.py

# Organize photos
python organize.py ~/Photos --dry-run
```

## Need It Working NOW?

If you can't wait for Vertex AI approval, temporarily use Anthropic API:

1. Get API key from https://console.anthropic.com (5 minutes)
2. Edit `.env`:
   ```
   USE_VERTEX_AI=false
   ANTHROPIC_API_KEY=sk-ant-api03-xxx...
   ```
3. Start organizing photos immediately!
4. Switch back to Vertex AI later when approved

---

**Start here:** https://console.cloud.google.com/vertex-ai/model-garden?project=itpc-gcp-product-all-claude
