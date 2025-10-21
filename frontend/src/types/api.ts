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
  requested_count: number
}

// Ответ от сервера после резервирования
export interface ReserveNumbersOut {
  session_id: string
  reserved_numbers: number[]
}

// Полезная нагрузка для резервирования конкретных номеров (админ)
export interface AdminReserveSpecific {
  equipment_id: number
  numbers: number[]
}

// Тип для назначения номера
export interface AssignNumberIn {
  session_id: string
  doc_name: string
  note: string | null
}

// Структура объекта 'created'
export interface CreatedDocumentInfo {
  id: number
  numeric: number
  formatted_no: string
  doc_name: string
  note: string | null
  reg_date: string
  equipment: EquipmentOut
  user: { id: number; username: string }
}

// Ответ от сервера после назначения
export interface AssignNumberOut {
  created: CreatedDocumentInfo
  message: string
}

// Для отображения уже назначенных номеров в сессии
export interface AssignedNumber {
  id: number
  numeric: number
  formatted_no: string
  doc_name: string
  note: string | null
}

// Структура одной строки в отчете
export interface ReportItem {
  id: number
  eq_type: string
  station_object: string
  factory_no: string | null
  station_no: string | null
  label: string | null
  doc_name: string
  doc_no: number
  user: string
  created: string
}

// Ответ от API с отчетом
export interface ReportResponse {
  totalItems: number
  items: ReportItem[]
}

// Полная информация о документе/оборудовании для админ-панели
export interface AdminDocumentRow {
  id: number
  doc_no: number
  reg_date: string
  doc_name: string
  note: string | null
  eq_id: number
  eq_type: string
  factory_no: string | null
  order_no: string | null
  label: string | null
  station_no: string | null
  station_object: string | null
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
  doc_name?: string
  date_from?: string
  date_to?: string
  eq_type?: string
  q?: string
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
