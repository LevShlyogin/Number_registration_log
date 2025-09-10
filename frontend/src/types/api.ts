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
