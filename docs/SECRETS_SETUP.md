# Setting Up Repository Secrets for GitHub Actions

The GitHub Actions workflows in this repository require API keys to be configured as repository secrets. This guide walks you through the setup process.

## Required Secrets

The `run-crewai-agents.yml` workflow requires two secrets:

1. **`OPENROUTER_API_KEY`** - OpenRouter API key for LLM access
2. **`MEM0_API_KEY`** - Mem0 API key for memory management

## Getting API Keys

### OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up or log in to your account
3. Navigate to [Keys](https://openrouter.ai/keys)
4. Click **Create Key**
5. Copy the generated key (starts with `sk-or-v1-`)

### Mem0 API Key

1. Go to [Mem0](https://mem0.ai/)
2. Sign up or log in to your account
3. Navigate to your [API Keys](https://app.mem0.ai/settings/api-keys) in settings
4. Generate a new API key
5. Copy the generated key

## Adding Secrets to GitHub Repository

### Step-by-Step Instructions

1. **Navigate to Repository Settings**
   - Go to your repository on GitHub
   - Click the **Settings** tab (you need admin access)

2. **Access Secrets and Variables**
   - In the left sidebar, expand **Secrets and variables**
   - Click **Actions**

3. **Add OPENROUTER_API_KEY**
   - Click **New repository secret**
   - Name: `OPENROUTER_API_KEY`
   - Secret: Paste your OpenRouter API key
   - Click **Add secret**

4. **Add MEM0_API_KEY**
   - Click **New repository secret** again
   - Name: `MEM0_API_KEY`
   - Secret: Paste your Mem0 API key
   - Click **Add secret**

### Verification

After adding both secrets, you should see them listed in the repository secrets:

```
OPENROUTER_API_KEY   Updated X minutes ago
MEM0_API_KEY         Updated X minutes ago
```

⚠️ **Note**: Secret values are hidden and cannot be viewed after creation. You can only update or delete them.

## Testing the Setup

Once secrets are configured:

1. Go to the **Actions** tab
2. Select **Run CrewAI Agents** workflow
3. Click **Run workflow**
4. Select the branch
5. Click **Run workflow** button

If secrets are configured correctly, the workflow will:
- ✅ Start successfully
- ✅ Configure environment variables
- ✅ Run CrewAI agents
- ✅ Upload artifacts

If you see errors related to missing API keys, verify:
- Secret names are exactly `OPENROUTER_API_KEY` and `MEM0_API_KEY` (case-sensitive)
- You have the correct permissions to access secrets in workflows
- The secrets were added to the correct repository

## Security Best Practices

### ✅ DO

- **Keep secrets confidential** - Never share API keys publicly
- **Use separate keys** - Use different keys for development and production
- **Rotate regularly** - Change keys periodically for security
- **Monitor usage** - Check OpenRouter and Mem0 dashboards for unusual activity
- **Set spending limits** - Configure usage caps in OpenRouter/Mem0 dashboards

### ❌ DON'T

- **Don't commit secrets** to the repository (use `.env` for local development)
- **Don't share workflow artifacts** that might contain sensitive data
- **Don't use production keys** in public repositories without caution
- **Don't bypass secret mechanisms** - Always use repository secrets for workflows

## Troubleshooting

### Error: "Secret not found"

**Cause**: Secret is not configured or has wrong name

**Solution**:
1. Check spelling: `OPENROUTER_API_KEY` and `MEM0_API_KEY` (exact case)
2. Verify you added secrets in Settings → Secrets and variables → Actions
3. Ensure you have admin access to the repository

### Error: "Authentication failed"

**Cause**: Invalid API key

**Solution**:
1. Verify the API key is correct
2. Check if the key has been revoked or expired
3. Regenerate key from OpenRouter/Mem0 dashboard
4. Update secret in GitHub

### Error: "Rate limit exceeded"

**Cause**: Too many API requests

**Solution**:
1. Check OpenRouter/Mem0 usage limits
2. Add credits to your account
3. Wait for rate limit to reset
4. Consider using a different model with higher limits

## Cost Management

### OpenRouter Costs

- Charges are based on tokens processed
- Different models have different rates
- Check current pricing: https://openrouter.ai/models
- Typical workflow run: $0.10 - $2.00 (depending on model)

**Recommended settings**:
- Start with smaller models for testing
- Monitor costs in OpenRouter dashboard
- Set spending alerts

### Mem0 Costs

- Charges based on memory operations
- Check pricing: https://mem0.ai/pricing
- Typical workflow run: minimal cost

## Updating Secrets

To update an existing secret:

1. Go to Settings → Secrets and variables → Actions
2. Click on the secret name
3. Click **Update secret**
4. Enter new value
5. Click **Update secret**

## Removing Secrets

To remove a secret:

1. Go to Settings → Secrets and variables → Actions
2. Click on the secret name
3. Click **Remove secret**
4. Confirm deletion

## Alternative: Use Environment Variables Locally

For local testing without GitHub Actions:

1. Copy `.env.example` to `.env`
2. Add your API keys:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   MEM0_API_KEY=your-mem0-key-here
   OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
   ```
3. Run `crewai run` locally

The `.env` file is gitignored and will not be committed.

## Further Reading

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [Workflows Guide](WORKFLOWS.md)
