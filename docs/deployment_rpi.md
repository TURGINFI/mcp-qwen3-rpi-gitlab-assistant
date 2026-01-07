# Raspberry Pi + Qwen3-0.6B Setup Notes

```bash
# 1. Clone the repository
git clone https://github.com/<your-name>/mcp-qwen3-rpi-gitlab-assistant.git
cd mcp-qwen3-rpi-gitlab-assistant

# 2. Create virtual environment
python -m venv mcp_venv
source mcp_venv/bin/activate # But I like to get in step by step

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set GitLab token (do NOT commit this)
export GITLAB_TOKEN="yourtoken"

# 5. Run the demo client
python -m src.mcp.main

**Note:**
- If you do not want to type the token every time, you can add the 'export GITLAB_TOKEN=...' line to your '~/.bashrc' on the Raspberry Pi. And make sure not to commit that file.
