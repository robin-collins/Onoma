# Azure OpenAI Setup Guide

This guide explains how to configure Onoma to work with Azure OpenAI services and deployments.

## Prerequisites

- An active Azure subscription
- Access to Azure OpenAI services
- A deployed Azure OpenAI model (e.g., GPT-4o, GPT-4, etc.)

## Configuration Options

Onoma supports both standard OpenAI and Azure OpenAI configurations. You can configure Azure OpenAI in two ways:

### Option 1: Configuration File

1. Generate a default configuration file:
   ```bash
   onomatool --save-config
   ```

2. Edit the `~/.onomarc` file to include your Azure OpenAI settings:
   ```toml
   # Set to true to use Azure OpenAI instead of standard OpenAI
   use_azure_openai = true

   # Your Azure OpenAI resource endpoint
   azure_openai_endpoint = "https://your-resource-name.openai.azure.com/"

   # Your Azure OpenAI API key
   azure_openai_api_key = "your-api-key-here"

   # API version (use the latest stable version)
   azure_openai_api_version = "2024-02-01"

   # Your deployment name (not the model name)
   azure_openai_deployment = "your-deployment-name"

   # Other settings remain the same
   default_provider = "openai"
   naming_convention = "snake_case"
   min_filename_words = 5
   max_filename_words = 15
   ```

### Option 2: Environment Variables

You can also configure Azure OpenAI using environment variables:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
```

Then set `use_azure_openai = true` in your configuration file.

## Azure OpenAI Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `use_azure_openai` | Enable Azure OpenAI (boolean) | `true` |
| `azure_openai_endpoint` | Your Azure OpenAI resource endpoint | `https://myresource.openai.azure.com/` |
| `azure_openai_api_key` | Your Azure OpenAI API key | `abcd1234...` |
| `azure_openai_api_version` | API version to use | `2024-02-01` |
| `azure_openai_deployment` | Your deployment name | `gpt-4o-deployment` |

## Important Notes

### Deployment Names vs Model Names

- **Deployment Name**: This is what you specify when creating a deployment in Azure OpenAI Studio (e.g., `my-gpt4-deployment`)
- **Model Name**: This is the underlying model (e.g., `gpt-4o`, `gpt-4`)

When using Azure OpenAI, Onoma uses your **deployment name** as the model parameter in API calls.

### API Versions

Azure OpenAI uses different API versions. The default is `2024-02-01`, but you can check the latest available versions in the [Azure OpenAI documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/reference).

## Example Configurations

### Basic Azure OpenAI Setup

```toml
# ~/.onomarc
use_azure_openai = true
azure_openai_endpoint = "https://mycompany-openai.openai.azure.com/"
azure_openai_api_key = "1234567890abcdef..."
azure_openai_deployment = "gpt4o-production"
default_provider = "openai"
naming_convention = "snake_case"
```

### Development vs Production

You might want different configurations for development and production:

**Development config** (`~/.onomarc-dev`):
```toml
use_azure_openai = true
azure_openai_endpoint = "https://dev-openai.openai.azure.com/"
azure_openai_deployment = "gpt4o-dev"
azure_openai_api_key = "dev-key-here"
```

**Production config** (`~/.onomarc-prod`):
```toml
use_azure_openai = true
azure_openai_endpoint = "https://prod-openai.openai.azure.com/"
azure_openai_deployment = "gpt4o-prod"
azure_openai_api_key = "prod-key-here"
```

Then use with:
```bash
onomatool --config ~/.onomarc-dev "*.pdf"
onomatool --config ~/.onomarc-prod "*.pdf"
```

## Troubleshooting

### Common Issues

1. **"Azure OpenAI endpoint is required"**
   - Ensure `azure_openai_endpoint` is set in your config or environment variables
   - Check that the endpoint URL is correct and includes `https://`

2. **"Azure OpenAI deployment name is required"**
   - Ensure `azure_openai_deployment` is set to your actual deployment name
   - Verify the deployment exists in your Azure OpenAI resource

3. **Authentication errors**
   - Verify your API key is correct
   - Check that your Azure OpenAI resource is active
   - Ensure you have the necessary permissions

4. **API version errors**
   - Try using a different API version (e.g., `2023-12-01-preview`)
   - Check Azure documentation for supported versions

### Debug Mode

Use the `--verbose` flag to see detailed configuration information:

```bash
onomatool --verbose "*.pdf"
```

This will show:
- Whether Azure OpenAI is being used
- The endpoint and deployment being used
- API version
- Request details

## Security Best Practices

1. **Use Environment Variables**: Store sensitive information like API keys in environment variables rather than config files
2. **Rotate Keys Regularly**: Regularly rotate your Azure OpenAI API keys
3. **Limit Permissions**: Use Azure RBAC to limit access to your OpenAI resources
4. **Separate Environments**: Use different Azure OpenAI resources for development and production

## Migration from Standard OpenAI

If you're migrating from standard OpenAI to Azure OpenAI:

1. Keep your existing configuration as backup
2. Add the Azure OpenAI settings to your config
3. Set `use_azure_openai = true`
4. Test with a few files first using `--dry-run`

Your existing prompts and naming conventions will work the same way with Azure OpenAI.