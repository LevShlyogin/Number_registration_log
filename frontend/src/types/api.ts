export interface EquipmentOut {
  id: number
  eq_type: string
  factory_no: string | null
  order_no: string | null
  label: string | null
  station_no: string | null
  station_object: string | null
  notes: string | null
}

export interface EquipmentIn {
  eq_type: string
  factory_no: string | null
  order_no: string | null
  label: string | null
  station_no: string | null
  station_object: string | null
  notes: string | null
}

// Тело запроса для резервирования номеров
export interface ReserveNumbersIn {
  equipment_id: number
  quantity: number
}

// Ответ от сервера после резервирования
export interface ReserveNumbersOut {
  session_id: string // UUID сессии
  reserved_numbers: number[]
}

// Тип для назначения номера (понадобится на следующем шаге)
export interface AssignNumberIn {
  session_id: string
  doc_name: string
  notes?: string
}

// Полезная нагрузка для резервирования конкретных номеров (админ)
export interface AdminReserveSpecific {
  equipment_id: number
  numbers: number[]
}

// Ответ от сервера после назначения
export interface AssignNumberOut {
  session_id: string
  doc_no: number
  doc_name: string
  created: string // ISO-строка даты
  user: string
}

// Для получения уже назначенных номеров в сессии
export interface AssignedNumber {
  doc_no: number
  doc_name: string
}

// Параметры для запроса отчета
export interface ReportParams {
  page: number
  itemsPerPage: number
  sortBy: { key: string; order: 'asc' | 'desc' }[]
  // Поля фильтров
  station_object?: string
  factory_no?: string
  date_from?: string // YYYY-MM-DD
  date_to?: string // YYYY-MM-DD
  q?: string // Глобальный поиск
}

// Структура одной строки в отчете
export interface ReportItem {
  id: number
  eq_type: string
  station_object: string
  factory_no: string | null
  doc_name: string
  doc_no: number
  user: string
  created: string // ISO-строка даты
}

// Ответ от API с отчетом
export interface ReportResponse {
  totalItems: number
  items: ReportItem[]
}

// Полная информация о документе/оборудовании для админ-панели
export interface AdminDocumentRow {
  id: number // ID документа
  doc_no: number
  reg_date: string // ISO-строка
  doc_name: string
  note: string | null
  // Данные связанного оборудования
  eq_id: number // ID оборудования
  eq_type: string
  factory_no: string | null
  order_no: string | null
  label: string | null
  station_no: string | null
  station_object: string | null
  // Данные пользователя
  username: string
}

// Универсальные параметры для поиска/фильтрации (используем и для отчетов, и для админки)
export interface SearchParams {
  page?: number
  itemsPerPage?: number
  sortBy?: { key: string; order: 'asc' | 'desc' }[]
  station_object?: string
  station_no?: string
  label?: string
  factory_no?: string
  order_no?: string
  username?: string
  session_id?: string
  date_from?: string
  date_to?: string
  eq_type?: string
  q?: string // Глобальный поиск
}

// Ответ от API для админского поиска
export interface AdminSearchResponse {
  items: AdminDocumentRow[]
  totalItems: number
}

// Полезная нагрузка для обновления документа (из AdminDocumentUpdate в schemas/admin.py)
export interface DocumentUpdatePayload {
  doc_name?: string
  note?: string
  eq_type?: string
  station_object?: string
  station_no?: string
  factory_no?: string
  order_no?: string
  label?: string
}
