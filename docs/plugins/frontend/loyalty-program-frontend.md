# Loyalty Program Plugin - Frontend Integration

## Übersicht

Kundenbindungsprogramm mit Punktesystem, Tier-System, Rewards und Marketing-Kampagnen.

## Key Components

### 1. Customer Loyalty Dashboard
```tsx
// Customer view of their loyalty status
- Points balance
- Tier status with progress bar
- Available rewards
- Transaction history
- QR code for scanning
```

### 2. Admin Dashboard
```tsx
// Management view
- Program statistics
- Active campaigns
- Tier distribution
- Redemption analytics
```

### 3. Point of Sale Integration
```tsx
// POS integration component
- Customer lookup by phone/email
- Point earning display
- Reward redemption
- Tier benefits applied
```

### 4. Rewards Management
```tsx
// Reward catalog
- Create/edit rewards
- Set point costs
- Validity periods
- Stock tracking
```

### 5. Campaign Manager
```tsx
// Marketing campaigns
- Bonus point campaigns
- Time-limited offers
- Target specific tiers
- Analytics dashboard
```

## Main Views

```tsx
// Customer Portal
export function CustomerLoyaltyPortal({ customerId }) {
  return (
    <div className="space-y-6">
      <TierStatusCard />
      <PointsBalanceCard />
      <AvailableRewardsList />
      <TransactionHistory />
      <QRCodeCard />
    </div>
  );
}

// Admin Management
export function LoyaltyAdminView() {
  return (
    <Tabs>
      <TabsList>
        <TabsTrigger>Dashboard</TabsTrigger>
        <TabsTrigger>Customers</TabsTrigger>
        <TabsTrigger>Rewards</TabsTrigger>
        <TabsTrigger>Campaigns</TabsTrigger>
        <TabsTrigger>Settings</TabsTrigger>
      </TabsList>
      {/* Tab contents */}
    </Tabs>
  );
}

// POS Integration Component
export function LoyaltyPOSWidget({ orderId, orderAmount }) {
  return (
    <Card>
      <CustomerLookup />
      <PointsEarned amount={orderAmount} />
      <AvailableRewardsQuickSelect />
      <ApplyButton />
    </Card>
  );
}
```

## Tier System Visualization

```tsx
export function TierProgressBar({ currentPoints, currentTier }) {
  const tiers = [
    { name: 'Bronze', threshold: 0, color: '#cd7f32' },
    { name: 'Silver', threshold: 1000, color: '#c0c0c0' },
    { name: 'Gold', threshold: 5000, color: '#ffd700' },
    { name: 'Platinum', threshold: 10000, color: '#e5e4e2' },
  ];

  return (
    <div className="relative">
      {/* Visual progress bar with tier milestones */}
      <ProgressBar value={currentPoints} max={nextTierThreshold} />
      <TierMilestones tiers={tiers} />
    </div>
  );
}
```

## API Hooks

```tsx
export function useCustomerLoyalty(customerId) {
  return useQuery({
    queryKey: ['loyalty', 'customer', customerId],
    queryFn: () => api.get(`/loyalty/customers/${customerId}`),
  });
}

export function useEarnPoints() {
  return useMutation({
    mutationFn: ({ customerId, amount }) =>
      api.post('/loyalty/earn', { customer_id: customerId, amount_spent: amount }),
  });
}

export function useRedeemReward() {
  return useMutation({
    mutationFn: ({ customerId, rewardId }) =>
      api.post('/loyalty/redeem', { customer_id: customerId, reward_id: rewardId }),
  });
}
```

## Features
- **4-Tier system (Bronze, Silver, Gold, Platinum)**
- **Point multipliers per tier**
- **Digital reward catalog**
- **QR code for customer identification**
- **Campaign management**
- **Analytics & ROI tracking**
- **Email/SMS notifications**
- **Birthday rewards**

## Routing
```tsx
/loyalty
  /dashboard - Admin overview
  /customers - Customer management
  /rewards - Reward catalog
  /campaigns - Marketing campaigns
  /analytics - Program analytics
  /settings - Tier & point configuration

// Customer portal
/my-loyalty - Customer's loyalty dashboard
```

## Integration Points
- **POS Checkout**: Automatic point calculation
- **Customer Profile**: Loyalty status display
- **Email Marketing**: Campaign notifications
- **Reports**: Loyalty program ROI
