-- Initial seed data for development

INSERT INTO tenants (id, name, code, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'Default Demo Tenant', 'demo-tenant', 'active')
ON CONFLICT (code) DO NOTHING;

INSERT INTO users (id, tenant_id, email, full_name, password_hash, is_tenant_admin)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'admin@demo.com',
    'Demo Admin User',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', -- password: admin123
    TRUE
)
ON CONFLICT (tenant_id, email) DO NOTHING;
