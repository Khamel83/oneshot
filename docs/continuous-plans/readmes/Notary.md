# Notary Platform - Vercel + Homelab Setup

**Status**: 🔄 Ready for Vercel Deployment
**Current Tier**: Homelab PostgreSQL + Vercel Serverless
**Upgrade Trigger**: > 50 appointments/day

## 🎯 What This Does

A modern mobile notary platform that handles:
- Online booking and scheduling
- Distance-based pricing with Google Maps
- Stripe payment processing (cards + Afterpay)
- Automated SMS/email reminders
- California compliance tracking
- Real-time availability management

## 🚀 Quick Start

### 1. Setup Homelab Database
```bash
cd homelab
cp .env.example .env
# Edit .env with your secure password
./scripts/setup.sh
```

### 2. Setup Vercel with SOPS Secrets
```bash
# Clone secrets vault if not already done
git clone git@github.com:Khamel83/secrets-vault.git ~/github/secrets-vault

# Decrypt your project secrets
sops --decrypt ~/github/secrets-vault/secrets.env.encrypted > .env

# Deploy to Vercel
npm i -g vercel
vercel --prod
```

## 🗄️ Architecture

### Frontend
- **Next.js 14** with App Router
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Server-side rendering** for performance

### Backend
- **Vercel Serverless Functions** (API routes)
- **Prisma ORM** with PostgreSQL
- **NextAuth.js** for authentication
- **Stripe** for payment processing

### Database (Homelab)
- **PostgreSQL 15** with connection pooling
- **PgBouncer** for serverless efficiency
- **Automated backups** with 30-day retention
- **Health monitoring** and alerts

### External Services
- **Stripe** - Payment processing
- **Google Maps API** - Distance calculations
- **Resend** - Email notifications
- **Twilio** - SMS notifications

## 🔧 Development

### Local Development
```bash
# Start homelab database
cd homelab && docker-compose up -d

# Setup environment
sops --decrypt ~/github/secrets-vault/secrets.env.encrypted > .env

# Initialize database
npx prisma generate && npx prisma db push

# Start development server
npm run dev
```

### Environment Variables (SOPS Managed)
All secrets managed via SOPS encrypted vault:
- Database connections
- API keys (Stripe, Google Maps, etc.)
- Email/SMS service credentials
- Authentication secrets

### Key Benefits of SOPS
- ✅ **Single source of truth**: One encrypted vault for all projects
- ✅ **Git-friendly**: Commit encrypted files safely
- ✅ **Team collaboration**: Share vault, not individual secrets
- ✅ **Audit trail**: Git history of encrypted changes

## 📊 Features

### For Clients
- **Real-time Pricing Calculator** - Instant quotes based on location and time
- **Online Booking** - Schedule appointments 24/7 with confirmation
- **Flexible Payments** - Credit cards or Afterpay (4 payments)
- **Service Tracking** - Real-time appointment status updates
- **Mobile-Responsive** - Works on all devices

### For Notary Operator
- **Dashboard** - Manage all appointments and clients
- **Automated Reminders** - SMS/email notifications
- **Document Management** - Upload and verify client documents
- **Journal Compliance** - California-required notary journal
- **Payment Tracking** - Real-time payment status

### California Compliance
- $15 maximum per signature (CA legal limit)
- Required journal entries for all notarizations
- Identification verification tracking
- Secure document storage
- Complete audit trail

## 💰 Pricing Model

### Base Fees
- **Notary Fee**: $15 per signature (California maximum)
- **Travel Fee**: $75 base mobile service fee
- **Distance**: First 10 miles free, then $0.50/mile

### Surcharges
- **After Hours** (6PM-9AM): +$50
- **Weekend** (Sat-Sun): +$25
- **Holidays**: +$100
- **Same Day**: +$50
- **Within 2 Hours**: +$100
- **Emergency/ASAP**: +$150

### Service Area
- Base Location: Thai Town, Los Angeles (90027)
- Coverage: All of LA County
- Maximum Distance: 50 miles from base

## Pricing Model

### Base Fees
- **Notary Fee**: $15 per signature (California maximum)
- **Travel Fee**: $75 base fee for mobile service
- **Distance**: First 10 miles free, then $0.50/mile

### Surcharges
- **After Hours** (6PM-9AM): +$50
- **Weekend** (Sat-Sun): +$25
- **Holidays**: +$100
- **Same Day**: +$50
- **Within 2 Hours**: +$100
- **Emergency/ASAP**: +$150

### Service Area
- Base Location: Thai Town, Los Angeles (90027)
- Coverage: All of LA County
- Maximum Distance: 50 miles from base

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- PostgreSQL database
- Stripe account (with Afterpay enabled)
- Google Maps API key (for distance calculation)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/notary-platform.git
   cd notary-platform
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```env
   DATABASE_URL="postgresql://user:password@localhost:5432/notary"
   NEXTAUTH_URL="http://localhost:3000"
   NEXTAUTH_SECRET="generate-with-openssl-rand-base64-32"
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
   STRIPE_SECRET_KEY="sk_test_..."
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY="your-api-key"
   ```

4. **Set up the database**
   ```bash
   npx prisma db push
   npx prisma generate
   ```

5. **Seed initial data** (optional)
   ```bash
   npx prisma db seed
   ```

6. **Run the development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment on Railway

### Quick Deploy

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize project**
   ```bash
   railway init
   ```

4. **Add PostgreSQL database**
   ```bash
   railway add --database postgres
   ```

5. **Set environment variables**
   ```bash
   railway variables set NEXTAUTH_SECRET=$(openssl rand -base64 32)
   railway variables set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_live_..."
   railway variables set STRIPE_SECRET_KEY="sk_live_..."
   railway variables set NEXT_PUBLIC_GOOGLE_MAPS_API_KEY="your-api-key"
   ```

6. **Deploy**
   ```bash
   railway up
   ```

### One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/yourusername/notary-platform)

## Stripe Setup

### Enable Afterpay

1. Log in to your [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Settings** → **Payment methods**
3. Find **Afterpay / Clearpay** and click **Enable**
4. No additional application or onboarding required!

### Test Afterpay

Use these test payment methods in development:
- **Afterpay Success**: Any email, phone: `+15555555555`
- **Afterpay Decline**: Phone: `+15555555556`

### Webhook Setup

1. Go to **Developers** → **Webhooks** in Stripe Dashboard
2. Add endpoint: `https://yourdomain.com/api/webhooks/stripe`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy webhook secret to `.env`:
   ```env
   STRIPE_WEBHOOK_SECRET="whsec_..."
   ```

## Google Maps Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable APIs:
   - Maps JavaScript API
   - Geocoding API
   - Distance Matrix API
4. Create credentials (API key)
5. Restrict API key to your domain
6. Add to `.env`:
   ```env
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY="your-api-key"
   ```

## Project Structure

```
notary-platform/
├── app/
│   ├── api/
│   │   ├── pricing/          # Pricing calculation API
│   │   └── create-payment-intent/  # Stripe payment API
│   ├── dashboard/            # Operator dashboard
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page with booking
│   └── globals.css           # Global styles
├── lib/
│   ├── pricing.ts            # Pricing calculation logic
│   ├── prisma.ts             # Database client
│   └── stripe.ts             # Stripe configuration
├── prisma/
│   └── schema.prisma         # Database schema
├── public/                   # Static assets
├── .env.example              # Environment variables template
├── next.config.js            # Next.js configuration
├── package.json              # Dependencies
├── railway.json              # Railway deployment config
└── README.md                 # This file
```

## Database Schema

### Key Models

- **User** - Client and operator accounts
- **Appointment** - Scheduled notary appointments
- **Document** - Uploaded documents for notarization
- **JournalEntry** - California-required notary journal
- **NotaryAvailability** - Operating hours configuration
- **PricingRule** - Dynamic pricing configuration

## API Routes

### POST `/api/pricing`
Calculate price for a notary appointment.

**Request:**
```json
{
  "numberOfSignatures": 2,
  "zip": "90027",
  "lat": 34.0978,
  "lng": -118.2930,
  "appointmentDate": "2025-11-24T14:00:00",
  "urgency": "same-day"
}
```

**Response:**
```json
{
  "success": true,
  "pricing": {
    "baseFee": 30.00,
    "travelFee": 75.00,
    "total": 155.00,
    "breakdown": [...]
  }
}
```

### POST `/api/create-payment-intent`
Create Stripe payment intent for appointment.

**Request:**
```json
{
  "amount": 155.00,
  "paymentMethod": "afterpay_clearpay",
  "appointmentDetails": {
    "date": "2025-11-24",
    "address": "123 Main St",
    "numberOfSignatures": 2
  }
}
```

## Configuration

### Update Business Details

Edit `.env` to customize:
```env
NOTARY_NAME="Your Business Name"
NOTARY_EMAIL="your@email.com"
NOTARY_PHONE="+1-555-0100"
NOTARY_COMMISSION_NUMBER="12345678"
BASE_LOCATION_ZIP="90027"
BASE_LOCATION_LAT="34.0978"
BASE_LOCATION_LNG="-118.2930"
```

### Customize Pricing

Edit `lib/pricing.ts` to adjust:
- Base fees
- Travel charges
- Distance rates
- Time surcharges
- Urgency fees

## Security

- All payments processed securely through Stripe
- Environment variables for sensitive data
- HTTPS enforced in production
- Input validation with Zod
- SQL injection protection via Prisma
- XSS protection via React

## Compliance

This platform is designed for **California notary public** operations:
- Follows California notary fee maximums
- Provides required journal entry system
- Tracks identification verification
- Maintains audit trails
- Complies with mobile notary regulations

**Always verify current California Secretary of State requirements.**

## Support

For issues or questions:
- Open an issue on GitHub
- Email: support@lamobilenotary.com
- Phone: (555) 010-0100

## License

Copyright © 2025 LA Mobile Notary. All rights reserved.

## Roadmap

- [ ] SMS notifications for appointment reminders
- [ ] Video notarization (RON) support
- [ ] Mobile app (iOS/Android)
- [ ] Multi-language support (Spanish, Korean, Thai)
- [ ] Automated email receipts
- [ ] Advanced reporting and analytics
- [ ] Integration with DocuSign
- [ ] Blockchain audit trail
- [ ] Client portal for document access

---

Built with ❤️ for mobile notaries in Los Angeles
