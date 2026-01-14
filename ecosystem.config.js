module.exports = {
  apps: [
    {
      name: 'masterpost-backend',
      script: '/bin/bash',
      args: '-c "cd /root/masterpost-saas/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"',
      cwd: '/root/masterpost-saas',
      interpreter: 'none',
      instances: 1,
      autorestart: true
    },
    {
      name: 'masterpost-frontend',
      script: '/usr/bin/npm',
      args: 'run dev -- -p 3001',
      cwd: '/root/masterpost-saas',
      interpreter: 'none',
      instances: 1,
      autorestart: true
    }
  ]
};
