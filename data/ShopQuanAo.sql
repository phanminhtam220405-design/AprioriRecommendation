CREATE DATABASE ShopBanQuanAo;
GO

USE ShopBanQuanAo;
GO

CREATE TABLE HoaDonBanHang (
    InvoiceID VARCHAR(20),
    ProductID VARCHAR(20),
    ProductName NVARCHAR(200),
    Category NVARCHAR(100),
    Size VARCHAR(10),
    Color NVARCHAR(50),
    Quantity INT,
    Price DECIMAL(18,2),
    OrderDate DATE
);
INSERT INTO HoaDonBanHang VALUES
('HD001','SP001',N'Áo thun nam basic',N'Áo thun','M',N'Đen',2,199000,'2025-01-01'),
('HD001','SP002',N'Quần jean nam slimfit',N'Quần jean','32',N'Xanh',1,499000,'2025-01-01'),

('HD002','SP003',N'Áo hoodie unisex',N'Hoodie','L',N'Trắng',1,450000,'2025-01-02'),
('HD002','SP004',N'Nón lưỡi trai',N'Phụ kiện','FreeSize',N'Đen',1,120000,'2025-01-02'),

('HD003','SP005',N'Áo sơ mi nữ',N'Sơ mi','S',N'Hồng',2,350000,'2025-01-03'),
('HD003','SP006',N'Chân váy tennis',N'Váy','M',N'Trắng',1,280000,'2025-01-03'),

('HD004','SP007',N'Áo khoác bomber',N'Áo khoác','XL',N'Xám',1,650000,'2025-01-04'),
('HD004','SP008',N'Quần jogger',N'Quần jogger','L',N'Đen',2,320000,'2025-01-04'),

('HD005','SP009',N'Áo croptop nữ',N'Croptop','S',N'Trắng',1,180000,'2025-01-05'),
('HD005','SP010',N'Quần short jean',N'Quần short','M',N'Xanh',1,250000,'2025-01-05'),

('HD006','SP011',N'Áo polo nam',N'Áo polo','L',N'Trắng',2,320000,'2025-01-06'),
('HD006','SP012',N'Quần kaki nam',N'Quần kaki','31',N'Kem',1,420000,'2025-01-06'),

('HD007','SP013',N'Áo len cổ lọ',N'Áo len','M',N'Nâu',1,390000,'2025-01-07'),
('HD007','SP014',N'Khăn choàng cổ',N'Phụ kiện','FreeSize',N'Be',1,150000,'2025-01-07'),

('HD008','SP015',N'Đầm nữ công sở',N'Đầm','M',N'Đỏ',1,550000,'2025-01-08'),
('HD008','SP016',N'Giày cao gót',N'Giày','37',N'Đen',1,620000,'2025-01-08'),

('HD009','SP017',N'Áo blazer nữ',N'Blazer','L',N'Kem',1,720000,'2025-01-09'),
('HD009','SP018',N'Quần tây nữ',N'Quần tây','M',N'Đen',1,410000,'2025-01-09'),

('HD010','SP019',N'Áo sweater unisex',N'Sweater','XL',N'Xám',2,360000,'2025-01-10'),
('HD010','SP020',N'Quần cargo',N'Quần cargo','32',N'Rêu',1,450000,'2025-01-10'),

('HD011','SP021',N'Áo ba lỗ nam',N'Áo tanktop','L',N'Trắng',3,150000,'2025-01-11'),
('HD011','SP022',N'Quần short thể thao',N'Quần short','L',N'Đen',2,220000,'2025-01-11'),

('HD012','SP023',N'Áo cardigan nữ',N'Cardigan','M',N'Hồng',1,430000,'2025-01-12'),
('HD012','SP024',N'Chân váy chữ A',N'Váy','S',N'Đen',1,290000,'2025-01-12'),

('HD013','SP025',N'Áo sơ mi caro',N'Sơ mi','XL',N'Xanh',2,340000,'2025-01-13'),
('HD013','SP026',N'Quần jean rách',N'Quần jean','33',N'Xanh',1,530000,'2025-01-13'),

('HD014','SP027',N'Áo thun oversize',N'Áo thun','XL',N'Trắng',1,260000,'2025-01-14'),
('HD014','SP028',N'Túi tote',N'Phụ kiện','FreeSize',N'Kem',1,180000,'2025-01-14'),

('HD015','SP029',N'Áo vest nam',N'Vest','L',N'Đen',1,950000,'2025-01-15'),
('HD015','SP030',N'Cà vạt',N'Phụ kiện','FreeSize',N'Đỏ',1,120000,'2025-01-15'),

('HD016','SP031',N'Áo khoác jean',N'Áo khoác','M',N'Xanh',1,580000,'2025-01-16'),
('HD016','SP032',N'Quần baggy nữ',N'Quần baggy','M',N'Đen',1,320000,'2025-01-16'),

('HD017','SP033',N'Áo giữ nhiệt',N'Áo giữ nhiệt','L',N'Đen',2,270000,'2025-01-17'),
('HD017','SP034',N'Quần legging',N'Legging','M',N'Đen',2,210000,'2025-01-17'),

('HD018','SP035',N'Áo sơ mi trắng',N'Sơ mi','M',N'Trắng',2,350000,'2025-01-18'),
('HD018','SP036',N'Chân váy bút chì',N'Váy','M',N'Đen',1,310000,'2025-01-18'),

('HD019','SP037',N'Áo hoodie zip',N'Hoodie','XL',N'Đen',1,490000,'2025-01-19'),
('HD019','SP038',N'Quần jogger túi hộp',N'Jogger','XL',N'Xám',1,390000,'2025-01-19'),

('HD020','SP039',N'Áo polo nữ',N'Áo polo','S',N'Hồng',1,280000,'2025-01-20'),
('HD020','SP040',N'Quần short kaki',N'Quần short','S',N'Kem',1,240000,'2025-01-20');
SELECT *
INSERT INTO HoaDonBanHang VALUES
('HD001','SP001',N'Áo thun nam basic',N'Áo thun','M',N'Đen',2,199000,'2025-01-01');

--Kiểm tra dữ liệu trùng--
SELECT InvoiceID, ProductID, ProductName, COUNT(*) AS SoLan
FROM HoaDonBanHang
GROUP BY InvoiceID, ProductID, ProductName
HAVING COUNT(*) > 1;
--Thêm dữ liệu thiếu
INSERT INTO HoaDonBanHang VALUES
('HD021','SP041',NULL,N'Áo thun','M',N'Đen',1,220000,'2025-01-21');

INSERT INTO HoaDonBanHang VALUES
('HD022','SP042',N'Quần jean baggy',N'Quần jean',NULL,N'Xanh',1,450000,'2025-01-22');
--Kiểm tra dữ liệu thiếu
SELECT *
FROM HoaDonBanHang
WHERE ProductName IS NULL
   OR Size IS NULL;

 --Tên SP chưa chuẩn--
 INSERT INTO HoaDonBanHang VALUES
('HD023','SP001',N'ao thun nam basic',N'Áo thun','M',N'Đen',1,199000,'2025-01-23');

INSERT INTO HoaDonBanHang VALUES
('HD024','SP001',N'ÁO THUN NAM BASIC',N'Áo thun','L',N'Trắng',1,199000,'2025-01-24');

--Kiểm tra
SELECT *
FROM HoaDonBanHang
WHERE ProductID = 'SP001';

--Tạo bảng clean
SELECT DISTINCT *
INTO HoaDonBanHang_Clean
FROM HoaDonBanHang;

--Xóa dữ liệu thiếu
DELETE FROM HoaDonBanHang_Clean
WHERE ProductName IS NULL
   OR Size IS NULL;
--chuẩn hóa tên
UPDATE HoaDonBanHang_Clean
SET ProductName = N'Áo thun nam basic'
WHERE ProductName IN (
    N'ao thun nam basic',
    N'ÁO THUN NAM BASIC'
);
--xóa khoảng trắng thừa
UPDATE HoaDonBanHang_Clean
SET ProductName = LTRIM(RTRIM(ProductName));

--KT sau xử lý
SELECT * FROM HoaDonBanHang_Clean;
--Tạo dữ liệu cho Apriori
SELECT InvoiceID, ProductName
INTO DuLieuApriori
FROM HoaDonBanHang_Clean;
SELECT * FROM DuLieuApriori;