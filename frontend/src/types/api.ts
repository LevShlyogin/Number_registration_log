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
