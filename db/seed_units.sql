-- Dummy data untuk modul Units (10 baris).
-- Aman dijalankan berulang: INSERT IGNORE melewati baris yang id/code-nya sudah ada.
-- Semua reference berawalan "UNSD" supaya mudah dihapus:
--   DELETE FROM units WHERE reference LIKE 'UNSD%';

INSERT IGNORE INTO units
  (id, reference, code, name, description, is_active, created_at, updated_at)
VALUES
  ('00000000-0000-4000-8000-000000000001', 'UNSD001', 'KG',   'Kilogram',   'Satuan berat dasar',          1, DATE_SUB(NOW(), INTERVAL 10 MINUTE), DATE_SUB(NOW(), INTERVAL 10 MINUTE)),
  ('00000000-0000-4000-8000-000000000002', 'UNSD002', 'G',    'Gram',       'Seperseribu kilogram',        1, DATE_SUB(NOW(), INTERVAL 9 MINUTE),  DATE_SUB(NOW(), INTERVAL 9 MINUTE)),
  ('00000000-0000-4000-8000-000000000003', 'UNSD003', 'L',    'Liter',      'Satuan volume cairan',        1, DATE_SUB(NOW(), INTERVAL 8 MINUTE),  DATE_SUB(NOW(), INTERVAL 8 MINUTE)),
  ('00000000-0000-4000-8000-000000000004', 'UNSD004', 'ML',   'Milliliter', 'Seperseribu liter',           1, DATE_SUB(NOW(), INTERVAL 7 MINUTE),  DATE_SUB(NOW(), INTERVAL 7 MINUTE)),
  ('00000000-0000-4000-8000-000000000005', 'UNSD005', 'M',    'Meter',      'Satuan panjang dasar',        1, DATE_SUB(NOW(), INTERVAL 6 MINUTE),  DATE_SUB(NOW(), INTERVAL 6 MINUTE)),
  ('00000000-0000-4000-8000-000000000006', 'UNSD006', 'CM',   'Centimeter', 'Seperseratus meter',          1, DATE_SUB(NOW(), INTERVAL 5 MINUTE),  DATE_SUB(NOW(), INTERVAL 5 MINUTE)),
  ('00000000-0000-4000-8000-000000000007', 'UNSD007', 'PCS',  'Pieces',     'Satuan per buah',             1, DATE_SUB(NOW(), INTERVAL 4 MINUTE),  DATE_SUB(NOW(), INTERVAL 4 MINUTE)),
  ('00000000-0000-4000-8000-000000000008', 'UNSD008', 'BOX',  'Box',        'Satuan per kotak',            1, DATE_SUB(NOW(), INTERVAL 3 MINUTE),  DATE_SUB(NOW(), INTERVAL 3 MINUTE)),
  ('00000000-0000-4000-8000-000000000009', 'UNSD009', 'DZN',  'Dozen',      'Satu lusin (12 buah)',        0, DATE_SUB(NOW(), INTERVAL 2 MINUTE),  DATE_SUB(NOW(), INTERVAL 2 MINUTE)),
  ('00000000-0000-4000-8000-000000000010', 'UNSD010', 'PACK', 'Pack',       NULL,                          1, DATE_SUB(NOW(), INTERVAL 1 MINUTE),  DATE_SUB(NOW(), INTERVAL 1 MINUTE));
