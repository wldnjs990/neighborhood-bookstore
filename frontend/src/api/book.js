import client from '@/api/client'

/**
 * 도서 목록 조회 (메인 페이지 - 베스트셀러 상위 10개)
 * GET /api/books/
 */
export const getBestSellerList = async () => {
  const response = await client.get('/api/books/')
  return response.data
}

/**
 * 도서 상세 조회
 * GET /api/books/:id/
 * @param {number} id - 도서 ID
 */
export const getBookDetail = async (id) => {
  const response = await client.get(`/api/books/${id}/`)
  return response.data
}

/**
 * 도서 북마크 토글 (등록/해제)
 * POST /api/books/:id/bookmarks/
 * @param {number} id - 도서 ID
 * @returns {Object} { is_bookmarked: boolean, message: string }
 */
export const toggleBookmark = async (id) => {
  const response = await client.post(`/api/books/${id}/bookmarks/`)
  return response.data
}

/**
 * 도서 평점 등록/수정
 * POST /api/books/:id/rating/
 * @param {number} id - 도서 ID
 * @param {number} score - 평점 (0.0 ~ 5.0)
 * @returns {Object} { message: string, average_rating: number, rating_count: number }
 */
export const rateBook = async (id, score) => {
  const response = await client.post(`/api/books/${id}/rating/`, { score })
  return response.data
}

/**
 * 도서 검색
 * GET /api/books/search/
 * @param {Object} params - 검색 파라미터
 * @param {string} params.search - 검색어
 * @param {string} params.searchType - 검색 타입 ('title' | 'author')
 * @param {Array<number>} params.categories - 카테고리 ID 배열
 * @param {boolean} params.adult - 성인 도서 포함 여부
 * @param {number} params.page - 페이지 번호
 * @param {number} params.size - 페이지당 개수 (기본: 25, 최대: 100)
 * @returns {Object} { count, next, previous, total_pages, results }
 */
export const searchBooks = async (params = {}) => {
  const response = await client.get('/api/books/search/', { params })
  return response.data
}

/**
 * 베스트셀러 목록 조회
 * GET /api/books/bestseller/
 * @param {Object} params - 페이지네이션 파라미터
 * @param {number} params.page - 페이지 번호
 * @param {number} params.size - 페이지당 개수 (기본: 50)
 * @returns {Object} { count, next, previous, total_pages, results }
 */
export const getBestSellers = async (params = {}) => {
  const response = await client.get('/api/books/bestseller/', { params })
  return response.data
}

/**
 * 내가 북마크한 도서 목록 조회
 * GET /api/books/bookmarked/
 * @returns {Array} 북마크한 도서 목록
 */
export const getBookmarkedBooks = async () => {
  const response = await client.get('/api/books/bookmarked/')
  return response.data
}

/**
 * 도서 자동완성 검색 (중고거래용)
 * GET /api/books/autocomplete/
 * @param {string} query - 검색어
 * @returns {Array} 최대 10개의 도서 목록
 */
export const autocompleteBook = async (query) => {
  const response = await client.get('/api/books/autocomplete/', {
    params: { q: query },
  })
  return response.data
}
