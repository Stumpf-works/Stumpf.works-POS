# Database Scripts

Utility scripts for database initialization, seeding, and maintenance.

## Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `init_db.py` | Initialize database with first tenant and admin | First deployment, fresh install |
| `seed_demo.py` | Populate database with demo data | Development, testing, demos |

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

## 1. Database Initialization (`init_db.py`)

Creates database tables, first tenant, and admin user.

### Usage

**Interactive Mode** (Recommended):
```bash
cd backend
python scripts/init_db.py
```

You will be prompted for:
- Tenant ID (slug): Unique identifier (e.g., "demo_store")
- Tenant Name: Display name (e.g., "Demo Store GmbH")
- Admin Username: Admin login name (default: "admin")
- Admin Email: Admin email address
- Admin Password: Strong password (hidden input)
- Admin First Name: Optional
- Admin Last Name: Optional

**Command Line Mode**:
```bash
python scripts/init_db.py \
  --tenant-slug my_store \
  --tenant-name "My Store" \
  --admin-username admin \
  --admin-email admin@mystore.com \
  --admin-password SecurePassword123 \
  --first-name John \
  --last-name Doe
```

### What It Does

1. ✅ Creates all database tables in public schema
2. ✅ Creates tenant record in `public.tenants` table
3. ✅ Creates dedicated PostgreSQL schema for tenant
4. ✅ Creates admin user with full permissions
5. ✅ Sets up initial configuration

### Example Output

```
🚀 Stumpf.works POS - Database Initialization
============================================================

📋 Creating database tables...
🏢 Creating tenant 'Demo Store' (demo_store)...
👤 Creating admin user 'admin'...

✅ Database initialization complete!

📝 Next steps:
   1. Login with: admin / yourpassword
   2. Configure TSE settings in admin dashboard
   3. Configure SumUp integration (if needed)
   4. Create product categories and products

💡 Access the API at: http://localhost:8000/api/docs
```

## 2. Demo Data Seeding (`seed_demo.py`)

Populates database with realistic demo data for testing.

### Usage

**Interactive Mode**:
```bash
cd backend
python scripts/seed_demo.py
```

**Command Line Mode**:
```bash
python scripts/seed_demo.py --tenant-slug demo_store
```

**Force Mode** (skip confirmation):
```bash
python scripts/seed_demo.py --tenant-slug demo_store --force
```

### What It Creates

**5 Product Categories:**
- 🥤 Getränke (Beverages)
- 🍕 Essen (Food)
- 🍫 Süßwaren (Sweets)
- 🚬 Tabakwaren (Tobacco)
- 📰 Sonstiges (Misc)

**15 Sample Products:**
- Various beverages (water, cola, beer, coffee)
- Food items (sandwiches, pretzels, currywurst)
- Candy (Snickers, Haribo, Milka)
- Tobacco products (Marlboro, Lucky Strike)
- Misc items (newspaper, lighter, tissues)

**3 Demo Users:**
- `cashier1` / `cashier123` (PIN: 1234) - Anna Schmidt
- `cashier2` / `cashier123` (PIN: 5678) - Max Müller
- `manager` / `manager123` (PIN: 9999) - Lisa Weber (Admin)

### Example Output

```
🌱 Stumpf.works POS - Demo Data Seeding
============================================================

This will add demo data to tenant 'demo_store'.
Continue? [y/N]: y

📁 Creating product categories...
📦 Creating 15 products...
👥 Creating 3 demo users...

✅ Demo data seeded successfully!

📝 Demo Users:
   - cashier1 / cashier123 (PIN: 1234)
   - cashier2 / cashier123 (PIN: 5678)
   - manager / manager123 (PIN: 9999)

💡 You can now test the POS with realistic data!
```

## Complete Setup Workflow

### For Development/Testing

```bash
# 1. Initialize database
python scripts/init_db.py

# 2. Seed demo data
python scripts/seed_demo.py --tenant-slug your_tenant_slug

# 3. Start the application
uvicorn app.main:app --reload
```

### For Production

```bash
# 1. Run migrations (instead of init_db.py)
alembic upgrade head

# 2. Initialize first tenant
python scripts/init_db.py

# 3. Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

⚠️ **Do NOT seed demo data in production!**

## Troubleshooting

### Error: "Tenant already exists"

The tenant was already created. To reset:

```sql
-- Connect to PostgreSQL
psql -U postgres -d pos_db

-- Drop tenant schema (CAREFUL!)
DROP SCHEMA IF EXISTS your_tenant_slug CASCADE;

-- Delete tenant record
DELETE FROM tenants WHERE slug = 'your_tenant_slug';
```

Then run init_db.py again.

### Error: "Database connection failed"

Check your `.env` file:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/pos_db
```

Verify PostgreSQL is running:
```bash
systemctl status postgresql
# or
docker-compose ps
```

### Error: "Module not found"

Make sure you're in the `backend` directory and have installed dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## Advanced Usage

### Multiple Tenants

```bash
# Create first tenant
python scripts/init_db.py \
  --tenant-slug store1 \
  --tenant-name "Store 1"

# Create second tenant (skip table creation)
python scripts/init_db.py \
  --tenant-slug store2 \
  --tenant-name "Store 2"
```

### Custom Product Data

Edit `seed_demo.py` to add your own products:

```python
DEMO_PRODUCTS = [
    {
        "name": "Your Product",
        "sku": "CUSTOM-001",
        "price": 9.99,
        "vat_rate": 19.0,
        "category": "Your Category",
        "stock": 100,
        "barcode": "1234567890123",
    },
    # ... more products
]
```

Then run:
```bash
python scripts/seed_demo.py --tenant-slug your_tenant
```

## Security Notes

⚠️ **Production Security:**

1. **Change Default Passwords**: Never use demo passwords in production
2. **Strong Passwords**: Use complex passwords for admin accounts
3. **Demo Users**: Delete or disable demo users in production
4. **Database Backups**: Always backup before running scripts
5. **Access Control**: Restrict script access to authorized personnel only

## Environment Variables

Required environment variables for scripts:

```bash
# .env file
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/database
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Maintenance Scripts (Future)

Planned additional scripts:

- `backup_db.py` - Automated database backups
- `cleanup_old_data.py` - Remove old transactions (GoBD compliant)
- `migrate_tenant.py` - Migrate tenant between schemas
- `export_tenant_data.py` - Export tenant data for archival

## Support

For issues or questions:

1. Check the logs: `tail -f logs/app.log`
2. Review database status: `python scripts/check_db_status.py`
3. Consult the documentation: `/docs`
4. Create an issue on GitHub

## License

Part of Stumpf.works POS System - See main LICENSE file
