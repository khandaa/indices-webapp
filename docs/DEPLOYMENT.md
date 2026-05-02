# Deployment Guide

This guide covers deployment options for the Indices Web Application to various hosting platforms.

## Overview

The application consists of:
- **Frontend**: React application (port 3050)
- **Backend**: FastAPI application (port 5050)
- **Database**: SQLite database

## Deployment Options

### 1. Vercel (Frontend) + Render (Backend) - Recommended

**Frontend Deployment:**
```bash
# Deploy frontend to Vercel
./deploy.sh vercel https://your-backend.onrender.com
```

**Backend Deployment:**
```bash
# Deploy backend to Render
./deploy.sh render
```

**Full Stack Deployment:**
```bash
# Deploy both frontend and backend
./deploy.sh full https://your-backend.onrender.com render
```

### 2. Vercel (Frontend) + Railway (Backend)

```bash
# Deploy to Railway
./deploy.sh full https://your-backend.onrender.com railway
```

### 3. Vercel (Frontend) + Heroku (Backend)

```bash
# Deploy to Heroku
./deploy.sh full https://your-backend.onrender.com heroku
```

### 4. Vercel (Frontend) + PythonAnywhere (Backend)

```bash
# Deploy to PythonAnywhere
./deploy.sh full https://your-backend.onrender.com pythonanywhere
```

## Prerequisites

### Required Tools
- **Node.js** (v16+)
- **npm** (v8+)
- **Python** (v3.8+)
- **Git** (for deployment platforms)

### Platform Accounts Required

#### Vercel
- Free account at [vercel.com](https://vercel.com)
- Connect GitHub repository

#### Render
- Free account at [render.com](https://render.com)
- Connect GitHub repository

#### Railway
- Free account at [railway.app](https://railway.app)
- Connect GitHub repository

#### Heroku
- Free account at [heroku.com](https://heroku.com)
- Connect GitHub repository

#### PythonAnywhere
- Account at [pythonanywhere.com](https://www.pythonanywhere.com)
- Install CLI tool

## Environment Configuration

### Frontend Environment Variables (.env.production)
```env
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_ENV=production
```

### Backend Environment Variables (.env)
```env
DATABASE_URL=sqlite:///database/index-database.db
CORS_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3050
ENVIRONMENT=production
```

## Deployment Commands

### Initialize Deployment
```bash
# Set up configuration files
./deploy.sh init
```

### Build Only
```bash
# Build frontend for production
./deploy.sh frontend
```

### Check Status
```bash
# Check all deployment statuses
./deploy.sh status
```

## Platform-Specific Considerations

### Vercel
- **Automatic deployments** from Git pushes
- **Preview URLs** for pull requests
- **Custom domains** supported
- **Edge functions** for server-side logic

### Render
- **Free tier** includes web service
- **Automatic deployments** from Git pushes
- **Background workers** for long-running tasks
- **Persistent storage** available

### Railway
- **Container-based** deployment
- **Automatic deployments** from Git pushes
- **Real-time logs** and metrics
- **Free tier** with credit system

### Heroku
- **Container-based** deployment
- **Add-ons** available for databases, logging
- **Automatic deployments** from Git pushes
- **Dyno scaling** for performance

### PythonAnywhere
- **Simple Python hosting**
- **Manual deployments**
- **SSH access** available
- **Custom domains** supported

## Troubleshooting

### Common Issues

#### CORS Errors
```bash
# Ensure CORS_ORIGINS includes frontend URL
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3050
```

#### Database Connection
```bash
# For SQLite, ensure database file path is correct
DATABASE_URL=sqlite:///database/index-database.db
```

#### Build Failures
```bash
# Clear node_modules and try again
rm -rf frontend/node_modules
./deploy.sh frontend
```

#### Deployment Failures
```bash
# Check logs for specific platform
./deploy.sh logs  # For Vercel
render logs          # For Render
heroku logs --tail    # For Heroku
```

## Production Considerations

### Security
- Use HTTPS URLs in production
- Set appropriate CORS origins
- Don't commit sensitive data to Git
- Use environment variables for secrets

### Performance
- Enable gzip compression on hosting platform
- Use CDN for static assets
- Monitor application performance

### Monitoring
- Set up health checks
- Monitor error rates
- Track response times
- Set up alerting for critical issues

## Advanced Configuration

### Custom Domain Setup
```bash
# For Vercel
vercel --prod

# For Render
# Add custom domain in Render dashboard

# For Railway
# Add custom domain in Railway dashboard
```

### SSL Certificates
All platforms provide automatic SSL certificates for custom domains.

### Backup Strategy
- Regular database backups
- Git version control
- Platform-specific backup solutions

## Cost Optimization

### Free Tier Limits
- **Vercel**: 100GB bandwidth/month
- **Render**: 750 hours/month free tier
- **Railway**: $5/month after free credits
- **Heroku**: 550-1000 dyno-hours/month

### Cost Saving Tips
- Use appropriate instance sizes
- Monitor resource usage
- Optimize bundle sizes
- Use caching strategies

## Migration Guide

### From Local to Production
1. **Update environment variables**
2. **Run database migrations**
3. **Test locally with production config**
4. **Deploy using preferred platform**
5. **Monitor initial performance**

### Blue-Green Deployments
```bash
# Deploy to staging first
./deploy.sh vercel https://staging-backend.onrender.com

# Test staging environment
# Then deploy to production
./deploy.sh vercel https://production-backend.onrender.com
```

## Support

### Platform Documentation
- [Vercel Docs](https://vercel.com/docs)
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://railway.app/docs)
- [Heroku Docs](https://devcenter.heroku.com/articles)
- [PythonAnywhere Docs](https://www.pythonanywhere.com/faq)

### Community Support
- Discord communities for each platform
- Stack Overflow for specific issues
- GitHub issues for application-specific problems
