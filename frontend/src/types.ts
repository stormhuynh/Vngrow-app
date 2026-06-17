export interface Customer {
  id: number;
  code: string;
  name: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  customer: Customer | null;
}

export interface ShipmentTask {
  id: number;
  name: string;
  date: string | null;
  actual_date: string | null;
  status: "pending" | "processing" | "done";
  status_display: string;
  note: string;
  order: number;
}

export interface ShipmentDocument {
  id: number;
  doc_type: string;
  doc_type_display: string;
  processing_status: string;
  processing_status_display: string;
  business_status: string;
  business_status_display: string;
  file: string | null;
  version: number;
  uploaded_by_name: string;
  uploaded_at: string;
}

export interface Payment {
  currency: string;
  total: string;
  paid: string;
  proof: string | null;
  note: string;
  updated_at: string;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  actor: string;
  action: string;
  detail: string;
}

export interface ShipmentListItem {
  id: number;
  code: string;
  direction: string;
  direction_display: string;
  mode: string;
  mode_display: string;
  op_status: string;
  op_status_display: string;
  current_task_name: string;
  current_task_status: string;
  current_task_status_display: string;
  origin: string;
  destination: string;
  etd: string | null;
  eta: string | null;
  carrier: string;
}

export interface ShipmentDetail extends ShipmentListItem {
  item_name: string;
  quantity: string;
  weight: string;
  cbm: string;
  container: string;
  vessel: string;
  voyage: string;
  si_cutoff: string | null;
  vgm_cutoff: string | null;
  tasks: ShipmentTask[];
  documents: ShipmentDocument[];
  payment: Payment | null;
  audit_logs: AuditLog[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
