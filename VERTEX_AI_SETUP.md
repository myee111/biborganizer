# Vertex AI Authentication Setup

This guide explains how to set up Google Cloud Vertex AI authentication to use Claude models through Google Cloud Platform.

## Prerequisites

- Google Cloud Platform account
- A GCP project with billing enabled
- `gcloud` CLI installed on your system

## Step 1: Install gcloud CLI

If you don't have the gcloud CLI installed:

**macOS:**
```bash
# Download and install
curl https://sdk.cloud.google.com | bash

# Restart your shell
exec -l $SHELL

# Initialize gcloud
gcloud init
```

**Linux:**
```bash
# Download and install
curl https://sdk.cloud.google.com | bash

# Restart your shell
exec -l $SHELL

# Initialize gcloud
gcloud init
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

## Step 2: Set Up Your GCP Project

```bash
# List your projects
gcloud projects list

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable the Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

## Step 3: Authenticate with Application Default Credentials

```bash
# This will open a browser window for authentication
gcloud auth application-default login
```

This command sets up credentials that the Anthropic SDK will automatically use.

## Step 4: Configure the Photo Organizer

Edit your `.env` file:

```bash
# Open .env file
nano .env
```

Add the following configuration:

```
USE_VERTEX_AI=true
VERTEX_PROJECT_ID=your-actual-gcp-project-id
VERTEX_REGION=us-east5
```

**Available Regions:**
- `us-east5` (recommended)
- `us-central1`
- `europe-west1`
- `asia-southeast1`

Choose the region closest to you for better performance.

## Step 5: Verify Setup

Run the installation test to verify everything is configured correctly:

```bash
source venv/bin/activate
python test_installation.py
```

You should see:
```
✓ VERTEX_PROJECT_ID found: your-project-id
✓ VERTEX_REGION: us-east5
Note: Make sure you're authenticated with gcloud
```

## Step 6: Test Claude Access

You can test that you can access Claude through Vertex AI:

```bash
# Create a simple test script
cat > test_vertex.py << 'EOF'
from claude_client import get_claude_client

client = get_claude_client()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello!"}]
)
print(response.content[0].text)
EOF

# Run the test
python test_vertex.py
```

If successful, you should see a greeting from Claude.

## Troubleshooting

### "Permission denied" or "403 Forbidden"

**Solution:** Make sure the Vertex AI API is enabled and you have the necessary IAM permissions:

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Check your permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"
```

You need one of these roles:
- `roles/aiplatform.user`
- `roles/aiplatform.admin`
- `roles/owner`

To add the role:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL" \
  --role="roles/aiplatform.user"
```

### "Application Default Credentials not found"

**Solution:** Run the authentication command:

```bash
gcloud auth application-default login
```

### "Project not found"

**Solution:** Verify your project ID is correct:

```bash
# List all projects
gcloud projects list

# Set the correct project
gcloud config set project YOUR_CORRECT_PROJECT_ID
```

### "Region not supported"

**Solution:** Use a supported region in your `.env`:

```
VERTEX_REGION=us-east5
```

## Cost Considerations

When using Vertex AI:
- Claude API calls are billed through your GCP account
- Pricing is similar to direct Anthropic API
- Check current pricing: https://cloud.google.com/vertex-ai/pricing
- Monitor usage in GCP Console under "Vertex AI" → "Usage"

## Switching Between Anthropic API and Vertex AI

You can easily switch between authentication methods by editing `.env`:

**Use Vertex AI:**
```
USE_VERTEX_AI=true
VERTEX_PROJECT_ID=your-project-id
VERTEX_REGION=us-east5
```

**Use Direct Anthropic API:**
```
USE_VERTEX_AI=false
ANTHROPIC_API_KEY=sk-ant-api03-xxx...
```

(Comment out or remove the line to use Anthropic API as default)

## Additional Resources

- [Google Cloud Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Anthropic Vertex AI Documentation](https://docs.anthropic.com/en/api/claude-on-vertex-ai)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)

## Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use separate projects** for dev/prod
3. **Enable audit logging** in GCP Console
4. **Set up budget alerts** to monitor costs
5. **Rotate credentials** regularly
6. **Use service accounts** for production deployments

For production use, consider using a service account instead of user credentials:

```bash
# Create service account
gcloud iam service-accounts create photo-organizer \
  --display-name="Photo Organizer Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:photo-organizer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/photo-organizer-key.json \
  --iam-account=photo-organizer@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/photo-organizer-key.json"
```
