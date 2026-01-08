# Complete Ollama Deployment Guide

## GPU Requirements for Server Deployment

### Hardware Requirements by Model

| Model | VRAM Needed | RAM Needed | GPU Examples | Performance | Cost |
|-------|-------------|------------|--------------|-------------|------|
| **Llama 3.1 8B (4-bit)** | **6GB** | 8GB | RTX 3060, RTX 4060 | 1-3s/report | **$300-500** |
| **Llama 3.1 8B (full)** | 16GB | 16GB | RTX 4080, RTX 4090 | 1-2s/report | $1,000-1,600 |
| **Llama 3.1 70B (4-bit)** | 40GB | 32GB | A6000, A100 | 3-5s/report | $3,000-10,000 |
| **CPU Only (8B)** | 0GB | 16GB | Any modern CPU | 30-60s/report | $0 (existing) |

### Recommended Setup for Production

**Best Value: RTX 4060 Ti (16GB)** - $500
- Runs Llama 3.1 8B perfectly
- 1-2 second response time
- Handles 100+ concurrent requests
- Low power consumption (160W)

**Enterprise: RTX 4090** - $1,600
- Runs Llama 3.1 8B at maximum speed
- Can handle 70B models (quantized)
- 500+ concurrent requests
- Best performance/cost ratio

---

## Server Deployment Options

### Option 1: Same Server (Simplest)

**Setup:**
- Run Ollama on same server as your FastAPI app
- Best for: Small-medium scale (<1000 requests/day)

**Pros:**
- ✅ Simple setup
- ✅ No network latency
- ✅ Single server to manage

**Cons:**
- ❌ Shares CPU/RAM with API
- ❌ Limited scalability

**Hardware:**
- CPU: 8+ cores
- RAM: 32GB (16GB for app + 16GB for Ollama)
- GPU: RTX 4060 Ti or better
- Storage: 50GB SSD

---

### Option 2: Dedicated LLM Server (Recommended)

**Setup:**
- Separate GPU server for Ollama
- FastAPI app on different server
- Connect via HTTP

**Pros:**
- ✅ Better performance
- ✅ Easy to scale (add more LLM servers)
- ✅ API server stays fast

**Cons:**
- ❌ Requires 2 servers
- ❌ Network latency (minimal)

**Architecture:**
```
[FastAPI Server]  →  HTTP  →  [Ollama Server (GPU)]
     (8GB RAM)                    (RTX 4060 Ti)
```

---

### Option 3: Cloud GPU Server

**Providers:**

| Provider | GPU | Cost/Hour | Monthly (24/7) |
|----------|-----|-----------|----------------|
| **RunPod** | RTX 4090 | $0.69 | ~$500 |
| **Vast.ai** | RTX 4090 | $0.40-0.80 | ~$300-600 |
| **Lambda Labs** | A6000 | $0.80 | ~$580 |
| **AWS EC2 g5** | A10G | $1.01 | ~$730 |

**Recommendation:** RunPod or Vast.ai for best value

---

## Complete Implementation Steps

### Step 1: Update Configuration Files

**File: `src/core/config.py`** ✅ (Already done)
```python
# Ollama settings added:
USE_OLLAMA: bool = False
OLLAMA_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "llama3.1:8b"
```

**File: `.env`** (Create or update)
```bash
# ============= OLLAMA CONFIGURATION =============
# Set to true to use local Ollama (zero API costs)
USE_OLLAMA=true

# Ollama server URL
# Local: http://localhost:11434
# Remote: http://your-gpu-server-ip:11434
OLLAMA_URL=http://localhost:11434

# Model to use (llama3.1:8b recommended for production)
OLLAMA_MODEL=llama3.1:8b

# ============= FALLBACK: GROQ API =============
# Keep GROQ as fallback if Ollama fails
GROQ_API_KEY=your_groq_key_here
LLM_MODEL=llama-3.3-70b-versatile

# ============= GITHUB APP (REQUIRED) =============
GITHUB_APP_ID=your_app_id
GITHUB_INSTALLATION_ID=your_installation_id
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nyour_key_here\n-----END RSA PRIVATE KEY-----"
```

### Step 2: Update LLM Service ✅ (Already done)

The `llm_service.py` has been updated with:
- Ollama priority in `__init__`
- New `_generate_with_ollama()` method
- Automatic fallback to GROQ

### Step 3: Install Ollama on Server

#### For Windows Server:

```powershell
# Download Ollama installer
# Visit: https://ollama.com/download/windows

# Or use PowerShell:
Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile "OllamaSetup.exe"

# Run installer
.\OllamaSetup.exe

# Pull Llama 3.1 8B model
ollama pull llama3.1:8b

# Verify installation
ollama list

# Test model
ollama run llama3.1:8b "Hello, how are you?"
```

#### For Linux Server (Ubuntu/Debian):

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# Verify
ollama list

# Test
ollama run llama3.1:8b "Hello"
```

#### For Docker Deployment:

```bash
# Pull Ollama Docker image
docker pull ollama/ollama

# Run with GPU support (NVIDIA)
docker run -d \
  --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

# Pull model inside container
docker exec -it ollama ollama pull llama3.1:8b

# Verify
docker exec -it ollama ollama list
```

### Step 4: Configure Ollama for Remote Access

If running Ollama on a separate server:

**Linux/Mac:**
```bash
# Edit systemd service
sudo systemctl edit ollama.service

# Add this:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

# Restart
sudo systemctl restart ollama
```

**Windows:**
```powershell
# Set environment variable
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'Machine')

# Restart Ollama service
Restart-Service Ollama
```

**Docker:**
```bash
docker run -d \
  --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  --name ollama \
  ollama/ollama
```

### Step 5: Update .env for Remote Ollama

```bash
# If Ollama is on different server
OLLAMA_URL=http://192.168.1.100:11434  # Replace with your server IP

# Or if using cloud
OLLAMA_URL=http://your-gpu-server.com:11434
```

### Step 6: Test the Integration

```bash
# Start your FastAPI server
cd d:\pp\Tringapps\Git-user_data-analyser
python src/main.py

# In another terminal, test the endpoint
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{\"github_input\": \"torvalds\"}"
```

**Expected Output:**
```
🚀 LLM Service: Ollama llama3.1:8b (Local, Zero Cost)
📍 Ollama URL: http://localhost:11434
🚀 Generating report with Ollama llama3.1:8b (local)...
✅ Ollama report generated successfully
```

### Step 7: Verify Fallback Works

```bash
# Stop Ollama temporarily
# Windows: Stop-Service Ollama
# Linux: sudo systemctl stop ollama

# Test again - should fallback to GROQ
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{\"github_input\": \"torvalds\"}"

# Expected:
# ❌ Cannot connect to Ollama
# 🔄 Falling back to GROQ...
# 🚀 Generating report with GROQ...
```

---

## Production Deployment Strategies

### Strategy 1: Local Development + Cloud Production

**Development (Your PC):**
```bash
USE_OLLAMA=true
OLLAMA_URL=http://localhost:11434
```

**Production (Cloud Server):**
```bash
USE_OLLAMA=true
OLLAMA_URL=http://gpu-server:11434
GROQ_API_KEY=backup_key  # Fallback
```

### Strategy 2: Hybrid (Ollama + GROQ)

**For 95% of requests:** Use Ollama (free)
**For premium users:** Use GROQ (better quality)

```python
# In your API endpoint
if user.tier == "premium":
    # Temporarily disable Ollama for this request
    os.environ["USE_OLLAMA"] = "false"
    report = llm_service.generate_report(data)
else:
    # Use Ollama
    report = llm_service.generate_report(data)
```

### Strategy 3: Load Balancing Multiple Ollama Servers

**Setup:**
```
[FastAPI] → [Load Balancer] → [Ollama Server 1]
                            → [Ollama Server 2]
                            → [Ollama Server 3]
```

**nginx config:**
```nginx
upstream ollama_backend {
    server ollama1:11434;
    server ollama2:11434;
    server ollama3:11434;
}

server {
    listen 11434;
    location / {
        proxy_pass http://ollama_backend;
    }
}
```

---

## Performance Optimization

### 1. Use Quantized Models (Recommended)

```bash
# 4-bit quantization (6GB VRAM, 90% quality)
ollama pull llama3.1:8b-q4_K_M

# 8-bit quantization (12GB VRAM, 95% quality)
ollama pull llama3.1:8b-q8_0

# Update .env
OLLAMA_MODEL=llama3.1:8b-q4_K_M
```

### 2. Adjust Context Length

```python
# In llm_service.py _generate_with_ollama
"options": {
    "temperature": self.temperature,
    "num_predict": self.max_tokens,
    "num_ctx": 4096  # Reduce for faster inference
}
```

### 3. Enable GPU Acceleration

```bash
# Verify GPU is being used
ollama ps

# Should show GPU memory usage
```

---

## Monitoring & Maintenance

### Check Ollama Status

```bash
# Linux
sudo systemctl status ollama

# Windows
Get-Service Ollama

# Docker
docker ps | grep ollama
```

### Monitor GPU Usage

```bash
# NVIDIA
nvidia-smi

# Watch in real-time
watch -n 1 nvidia-smi
```

### Logs

```bash
# Linux
sudo journalctl -u ollama -f

# Docker
docker logs -f ollama
```

---

## Cost Comparison

### Current Setup (GROQ API)
- 10,000 reports/month = **$2,700**
- 100,000 reports/month = **$27,000**

### With Ollama (Local)
- Hardware: **$500** (RTX 4060 Ti) one-time
- Electricity: ~$10/month (160W × 24/7)
- **Total first month: $510**
- **Ongoing: $10/month**

**ROI: Break-even in 1 week!**

### With Cloud GPU (RunPod)
- RTX 4090: **$500/month** (24/7)
- Still **$2,200/month savings** vs GROQ
- No upfront hardware cost

---

## Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama
# Windows: Start-Service Ollama
# Linux: sudo systemctl start ollama
# Docker: docker start ollama
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model
ollama pull llama3.1:8b

# Verify
ollama list
```

### Issue: "Out of memory"

**Solution:**
```bash
# Use smaller/quantized model
ollama pull llama3.1:8b-q4_K_M

# Update .env
OLLAMA_MODEL=llama3.1:8b-q4_K_M
```

### Issue: Slow generation (>10s)

**Solution:**
- Check GPU is being used: `nvidia-smi`
- Reduce context: `num_ctx=2048`
- Use quantized model
- Upgrade GPU

---

## Next Steps

1. ✅ Code updated (config.py + llm_service.py)
2. ⏳ Install Ollama on your server
3. ⏳ Pull llama3.1:8b model
4. ⏳ Update .env file
5. ⏳ Test integration
6. ⏳ Deploy to production

**Ready to install Ollama?**
