<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import api, { fileBase } from "@/api";
import type {
  Paginated,
  ShipmentDetail,
  ShipmentDocument,
  ShipmentListItem,
} from "@/types";

const list = ref<ShipmentListItem[]>([]);
const selected = ref<ShipmentDetail | null>(null);
const loadingList = ref(false);
const loadingDetail = ref(false);

const filters = ref({
  direction: "",
  mode: "",
  ordering: "eta",
});

const directions = [
  { value: "", label: "Tất cả" },
  { value: "export", label: "Export" },
  { value: "import", label: "Import" },
];
const modes = [
  { value: "", label: "Tất cả" },
  { value: "fcl", label: "FCL" },
  { value: "lcl", label: "LCL" },
  { value: "air", label: "Air cargo" },
  { value: "express", label: "Express" },
];
const orderings = [
  { value: "eta", label: "ETA gần nhất" },
  { value: "etd", label: "ETD gần nhất" },
];

const docTypes = [
  { value: "invoice", label: "Hóa đơn thương mại - Commercial Invoice" },
  { value: "packing", label: "Packing list - Phiếu đóng gói" },
  { value: "co", label: "Chứng nhận xuất xứ - Certificate of Origin" },
  { value: "bill", label: "Vận đơn - Bill of Lading" },
  { value: "contract", label: "Sales contract / Proforma invoice" },
  { value: "other", label: "Khác" },
];

const latestDocuments = computed<ShipmentDocument[]>(() => {
  if (!selected.value) return [];
  const latest = new Map<string, ShipmentDocument>();
  selected.value.documents.forEach((document) => {
    const current = latest.get(document.doc_type);
    if (!current || document.version > current.version) {
      latest.set(document.doc_type, document);
    }
  });
  return Array.from(latest.values());
});

async function fetchList() {
  loadingList.value = true;
  try {
    const params: Record<string, string> = { ordering: filters.value.ordering };
    if (filters.value.direction) params.direction = filters.value.direction;
    if (filters.value.mode) params.mode = filters.value.mode;
    const res = await api.get<Paginated<ShipmentListItem>>("/shipments/", {
      params,
    });
    list.value = res.data.results;
    if (list.value.length && !selected.value) {
      selectShipment(list.value[0].id);
    }
  } finally {
    loadingList.value = false;
  }
}

async function selectShipment(id: number) {
  loadingDetail.value = true;
  try {
    const res = await api.get<ShipmentDetail>(`/shipments/${id}/`);
    selected.value = res.data;
  } finally {
    loadingDetail.value = false;
  }
}

function fmtDate(d: string | null) {
  if (!d) return "--";
  const date = new Date(d);
  return date.toLocaleDateString("vi-VN");
}

function fmtDateTime(d: string | null) {
  if (!d) return "--";
  const date = new Date(d);
  return date.toLocaleString("vi-VN");
}

function fmtMoney(v: string | undefined, currency = "VND") {
  if (v === undefined) return "--";
  const n = Number(v);
  return n.toLocaleString("vi-VN") + " " + currency;
}

// Upload modal
const showUpload = ref(false);
const uploadDocType = ref("invoice");
const uploadFile = ref<File | null>(null);
const uploading = ref(false);

function openUpload() {
  uploadDocType.value = "invoice";
  uploadFile.value = null;
  showUpload.value = true;
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  uploadFile.value = target.files?.[0] || null;
}

async function submitUpload() {
  if (!selected.value || !uploadFile.value) return;
  uploading.value = true;
  try {
    const form = new FormData();
    form.append("doc_type", uploadDocType.value);
    form.append("file", uploadFile.value);
    await api.post(`/shipments/${selected.value.id}/documents/`, form);
    showUpload.value = false;
    await selectShipment(selected.value.id);
  } finally {
    uploading.value = false;
  }
}

watch(
  () => [filters.value.direction, filters.value.mode, filters.value.ordering],
  () => fetchList()
);

onMounted(fetchList);
</script>

<template>
  <div>
    <div class="top">
      <b>Shipment</b>
      <div class="muted">Theo dõi lô hàng, chứng từ và thanh toán</div>
    </div>
    <div class="content">
      <div class="split">
        <!-- LEFT: list + filters -->
        <div>
          <div class="card filters">
            <div class="field">
              <label>Chiều</label>
              <div class="chips">
                <span
                  v-for="d in directions"
                  :key="d.value"
                  class="chip"
                  :class="{ active: filters.direction === d.value }"
                  @click="filters.direction = d.value"
                  >{{ d.label }}</span
                >
              </div>
            </div>
            <div class="field">
              <label>Loại hình</label>
              <div class="chips">
                <span
                  v-for="m in modes"
                  :key="m.value"
                  class="chip"
                  :class="{ active: filters.mode === m.value }"
                  @click="filters.mode = m.value"
                  >{{ m.label }}</span
                >
              </div>
            </div>
            <div class="field">
              <label>Sắp xếp</label>
              <div class="chips">
                <span
                  v-for="o in orderings"
                  :key="o.value"
                  class="chip"
                  :class="{ active: filters.ordering === o.value }"
                  @click="filters.ordering = o.value"
                  >{{ o.label }}</span
                >
              </div>
            </div>
          </div>

          <div class="shipment-list" style="margin-top: 12px">
            <div v-if="loadingList" class="muted">Đang tải...</div>
            <div
              v-for="s in list"
              :key="s.id"
              class="shipment-card"
              :class="{ active: selected?.id === s.id }"
              @click="selectShipment(s.id)"
            >
              <div class="route">
                <span>{{ s.origin || "--" }}</span>
                <span class="arrow">&#8594;</span>
                <span>{{ s.destination || "--" }}</span>
              </div>
              <div class="row" style="justify-content: space-between">
                <b>{{ s.code }}</b>
                <span class="tag">{{ s.mode_display }}</span>
              </div>
              <div class="row" style="justify-content: space-between">
                <span class="muted">{{ s.direction_display }}</span>
                <span>
                  <span class="dot" :class="s.current_task_status || 'processing'"></span>
                  {{ s.current_task_name || s.op_status_display }}
                </span>
              </div>
              <div class="muted">ETD {{ fmtDate(s.etd) }} · ETA {{ fmtDate(s.eta) }}</div>
            </div>
            <div v-if="!loadingList && !list.length" class="empty">
              Chưa có lô hàng phù hợp bộ lọc.
            </div>
          </div>
        </div>

        <!-- RIGHT: detail -->
        <div v-if="selected" class="detail">
          <div class="grid g2">
            <div class="card">
              <h2>Mô tả hàng hóa</h2>
              <div class="muted">Tên hàng: <b>{{ selected.item_name || "--" }}</b></div>
              <div class="muted">Số lượng: <b>{{ selected.quantity || "--" }}</b></div>
              <div class="muted">Trọng lượng: <b>{{ selected.weight || "--" }}</b></div>
              <div class="muted">CBM: <b>{{ selected.cbm || "--" }}</b></div>
              <div class="muted">Container: <b>{{ selected.container || "--" }}</b></div>
            </div>
            <div class="card">
              <h2>Thông tin vận chuyển</h2>
              <div class="muted">ETD: <b>{{ fmtDate(selected.etd) }}</b></div>
              <div class="muted">ETA: <b>{{ fmtDate(selected.eta) }}</b></div>
              <div class="muted">Vessel: <b>{{ selected.vessel || "--" }}</b></div>
              <div class="muted">Voyage: <b>{{ selected.voyage || "--" }}</b></div>
              <div class="muted">Carrier: <b>{{ selected.carrier || "--" }}</b></div>
            </div>
          </div>

          <!-- Tasks -->
          <div class="card">
            <div class="head"><h2>Tiến độ công việc</h2></div>
            <div class="table tasks-table">
              <table>
                <thead>
                  <tr>
                    <th>Công việc</th>
                    <th>Lịch trình</th>
                    <th>Trạng thái</th>
                    <th>Ghi chú</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in selected.tasks" :key="t.id">
                    <td>{{ t.name }}</td>
                    <td :class="t.actual_date ? 'time-actual' : 'time-estimate'">
                      {{ fmtDate(t.actual_date || t.date) }}
                    </td>
                    <td><span class="dot" :class="t.status"></span>{{ t.status_display }}</td>
                    <td class="muted">{{ t.note || "--" }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Documents -->
          <div class="card">
            <div class="head">
              <h2>Hồ sơ &amp; chứng từ</h2>
              <button class="small" @click="openUpload">+ Tải lên chứng từ</button>
            </div>
            <div class="table">
              <table>
                <thead>
                  <tr>
                    <th>Loại chứng từ</th>
                    <th>Trạng thái xử lý</th>
                    <th>File</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="d in latestDocuments" :key="d.id">
                    <td>{{ d.doc_type_display }}</td>
                    <td><span class="tag">{{ d.processing_status_display }}</span></td>
                    <td>
                      <a v-if="d.file" :href="fileBase + d.file" target="_blank">
                        <button class="small ghost">Tải xuống</button>
                      </a>
                      <span v-else class="muted">Chưa có</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Payment -->
          <div class="card" v-if="selected.payment">
            <div class="head"><h2>Thanh toán</h2></div>
            <div class="grid g3">
              <div class="muted">Tổng tiền: <b>{{ fmtMoney(selected.payment.total, selected.payment.currency) }}</b></div>
              <div class="muted">Đã thanh toán: <b>{{ fmtMoney(selected.payment.paid, selected.payment.currency) }}</b></div>
              <div class="muted">Ghi chú: <b>{{ selected.payment.note || "--" }}</b></div>
            </div>
            <div class="row">
              <button class="small ghost">Upload ủy nhiệm chi</button>
            </div>
          </div>

          <!-- Audit log -->
          <div class="card">
            <div class="head"><h2>Lịch sử ghi nhận thay đổi</h2></div>
            <div class="table audit-table">
              <table>
                <thead>
                  <tr>
                    <th>Thời gian</th>
                    <th>Người thực hiện</th>
                    <th>Hành động</th>
                    <th>Chi tiết</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in selected.audit_logs" :key="a.id">
                    <td>{{ fmtDateTime(a.timestamp) }}</td>
                    <td>{{ a.actor }}</td>
                    <td>{{ a.action }}</td>
                    <td class="muted">{{ a.detail }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else class="empty">Chọn một lô hàng để xem chi tiết.</div>
      </div>
    </div>

    <!-- Upload modal -->
    <div v-if="showUpload" class="modal-mask" @click.self="showUpload = false">
      <div class="modal">
        <div class="head"><h2>Tải lên chứng từ</h2></div>
        <div class="field">
          <label>Loại chứng từ</label>
          <select class="control" v-model="uploadDocType">
            <option v-for="dt in docTypes" :key="dt.value" :value="dt.value">
              {{ dt.label }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>Chọn file</label>
          <input class="control" type="file" @change="onFileChange" />
        </div>
        <div class="row" style="justify-content: flex-end">
          <button class="ghost" @click="showUpload = false">Hủy</button>
          <button :disabled="!uploadFile || uploading" @click="submitUpload">
            {{ uploading ? "Đang tải..." : "Tải lên" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
