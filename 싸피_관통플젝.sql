-- 싸피 관통 프로젝트 - CASCADE 및 오류 수정본
-- 모든 문법 오류 수정 + CASCADE 추가

-- ============================================
-- 1. User 테이블 (가장 먼저 생성)
-- ============================================
CREATE TABLE `user` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`username` VARCHAR(150) NOT NULL UNIQUE COMMENT '로그인 아이디',
	`email` VARCHAR(254) NOT NULL,
	`password` VARCHAR(128) NOT NULL,
	`nickname` VARCHAR(50) NOT NULL UNIQUE,
	`book_mbti` VARCHAR(4) NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='사용자';

-- ============================================
-- 2. Category 테이블
-- ============================================
CREATE TABLE `category` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NOT NULL UNIQUE COMMENT '카테고리명',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='도서 카테고리';

-- ============================================
-- 3. Book 테이블
-- ============================================
CREATE TABLE `book` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`category_id` INTEGER NULL COMMENT 'FK - category',
	`isbn` VARCHAR(13) NOT NULL UNIQUE COMMENT 'ISBN-13, 유니크',
	`title` VARCHAR(200) NOT NULL COMMENT '도서명',
	`author` VARCHAR(200) NOT NULL,
	`publisher` VARCHAR(100) NOT NULL,
	`pub_date` DATE NULL,
	`category_name` VARCHAR(200) NULL COMMENT '알라딘 원본 카테고리',
	`cover` VARCHAR(500) NULL COMMENT '표지 이미지 URL',
	`description` TEXT NULL,
	`price_standard` INTEGER NOT NULL DEFAULT 0 COMMENT '정가 (원)',
	`price_sales` INTEGER NOT NULL DEFAULT 0 COMMENT '판매가 (원)',
	`adult` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '성인 도서 여부',
	`item_id` INTEGER NULL COMMENT '알라딘 상품 ID',
	`mall_type` VARCHAR(20) NULL,
	`rating_count` INTEGER NOT NULL DEFAULT 0 COMMENT '우리 서비스 평점 개수 (book_rating에서 계산)',
	`average_rating` DECIMAL(3,2) NOT NULL DEFAULT 0.00 COMMENT '우리 서비스 평균 평점 (book_rating에서 계산, 0.00~5.00)',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	-- FK: Category → Book (카테고리 삭제 시 book의 category_id만 NULL)
	CONSTRAINT `FK_category_TO_book` FOREIGN KEY (`category_id`)
		REFERENCES `category` (`id`)
		ON DELETE SET NULL
		ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='도서';

-- ============================================
-- 4. BookRating 테이블 (식별관계 - 복합 PK)
-- ============================================
CREATE TABLE `book_rating` (
	`user_id` INTEGER NOT NULL,
	`book_id` INTEGER NOT NULL,
	`score` DECIMAL(2,1) NOT NULL COMMENT '평점 (0.0~5.0)',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`user_id`, `book_id`),
	-- FK: User → BookRating (사용자 삭제 시 평점도 삭제)
	CONSTRAINT `FK_user_TO_book_rating` FOREIGN KEY (`user_id`)
		REFERENCES `user` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	-- FK: Book → BookRating (책 삭제 시 평점도 삭제)
	CONSTRAINT `FK_book_TO_book_rating` FOREIGN KEY (`book_id`)
		REFERENCES `book` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	-- 체크 제약: 평점 범위 0.0~5.0
	CONSTRAINT `CHK_score_range` CHECK (`score` >= 0.0 AND `score` <= 5.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='도서 평점';

-- ============================================
-- 5. Bookmark 테이블 (식별관계 - 복합 PK)
-- ============================================
CREATE TABLE `bookmark` (
	`user_id` INTEGER NOT NULL,
	`book_id` INTEGER NOT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`user_id`, `book_id`),
	-- FK: User → Bookmark (사용자 삭제 시 북마크도 삭제)
	CONSTRAINT `FK_user_TO_bookmark` FOREIGN KEY (`user_id`)
		REFERENCES `user` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	-- FK: Book → Bookmark (책 삭제 시 북마크도 삭제)
	CONSTRAINT `FK_book_TO_bookmark` FOREIGN KEY (`book_id`)
		REFERENCES `book` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='북마크';

-- ============================================
-- 6. Trade 테이블 (중고거래)
-- ============================================
CREATE TABLE `trade` (
	`id` INTEGER NOT NULL AUTO_INCREMENT,
	`user_id` INTEGER NOT NULL COMMENT '판매자 ID',
	`book_id` INTEGER NOT NULL COMMENT '판매할 도서 ID',
	`title` VARCHAR(200) NOT NULL COMMENT '판매글 제목',
	`content` TEXT NOT NULL COMMENT '판매글 내용',
	`sale_type` VARCHAR(10) NOT NULL DEFAULT 'sale' COMMENT 'sale 또는 free',
	`price` INTEGER NOT NULL DEFAULT 0 COMMENT '판매가격',
	`region` VARCHAR(50) NOT NULL COMMENT '거래 지역',
	`status` VARCHAR(20) NOT NULL DEFAULT 'available' COMMENT 'available, reserved, sold',
	`image` VARCHAR(500) NULL COMMENT '상품 이미지 파일 경로',
	`kakao_chat_url` VARCHAR(100) NULL COMMENT '카카오톡 오픈채팅 URL',
	`view_count` INTEGER NOT NULL DEFAULT 0 COMMENT '조회수',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	-- FK: User → Trade (사용자 삭제 시 거래글도 삭제)
	CONSTRAINT `FK_user_TO_trade` FOREIGN KEY (`user_id`)
		REFERENCES `user` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	-- FK: Book → Trade (책 삭제 시 거래글도 삭제)
	CONSTRAINT `FK_book_TO_trade` FOREIGN KEY (`book_id`)
		REFERENCES `book` (`id`)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	-- 체크 제약: sale_type 값 제한
	CONSTRAINT `CHK_sale_type` CHECK (`sale_type` IN ('sale', 'free')),
	-- 체크 제약: status 값 제한
	CONSTRAINT `CHK_status` CHECK (`status` IN ('available', 'reserved', 'sold'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='중고거래';

-- ============================================
-- 인덱스 추가 (성능 최적화)
-- ============================================

-- Book 테이블 인덱스
CREATE INDEX `idx_book_category` ON `book`(`category_id`);
CREATE INDEX `idx_book_isbn` ON `book`(`isbn`);
CREATE INDEX `idx_book_rating` ON `book`(`average_rating` DESC);
CREATE INDEX `idx_book_created` ON `book`(`created_at` DESC);

-- Trade 테이블 인덱스
CREATE INDEX `idx_trade_user` ON `trade`(`user_id`);
CREATE INDEX `idx_trade_book` ON `trade`(`book_id`);
CREATE INDEX `idx_trade_status` ON `trade`(`status`);
CREATE INDEX `idx_trade_created` ON `trade`(`created_at` DESC);
CREATE INDEX `idx_trade_region` ON `trade`(`region`);

-- BookRating 테이블 인덱스
CREATE INDEX `idx_book_rating_book` ON `book_rating`(`book_id`);
CREATE INDEX `idx_book_rating_score` ON `book_rating`(`score` DESC);

-- Bookmark 테이블 인덱스
CREATE INDEX `idx_bookmark_book` ON `bookmark`(`book_id`);

-- ============================================
-- CASCADE 설정 요약
-- ============================================
/*
✅ User 삭제 시:
   → book_rating 삭제 (CASCADE)
   → bookmark 삭제 (CASCADE)
   → trade 삭제 (CASCADE)

✅ Book 삭제 시:
   → book_rating 삭제 (CASCADE)
   → bookmark 삭제 (CASCADE)
   → trade 삭제 (CASCADE)

✅ Category 삭제 시:
   → book의 category_id만 NULL (SET NULL)
   → book 자체는 유지

✅ 식별관계 (복합 PK):
   - book_rating: (user_id, book_id)
   - bookmark: (user_id, book_id)
   → 중복 방지!

✅ 비식별관계 (독립 PK):
   - trade: id (같은 사람이 같은 책을 여러 번 판매 가능)
*/
