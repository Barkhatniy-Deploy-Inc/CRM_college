<template>
  <div class="schedule-container">
    <header class="schedule-header">
      <div class="title-section">
        <div class="header-main">
          <h1>Расписание занятий</h1>
          <div v-if="isAdmin" class="editor-toggle">
            <span class="label">Режим конструктора</span>
            <label class="switch">
              <input type="checkbox" v-model="isEditMode">
              <span class="slider"></span>
            </label>
          </div>
        </div>
        <div class="week-info">
          <span class="date-range">{{ formattedDateRange }}</span>
          <span class="week-type badge">{{ isEvenWeek ? 'Четная неделя' : 'Нечетная неделя' }}</span>
        </div>
      </div>

      <div class="controls-section glass-panel">
        <div class="navigation">
          <BaseButton variant="outline" @click="prevWeek" class="nav-btn">
            <AppIcon name="chevron-left" size="18" />
            <span>Пред.</span>
          </BaseButton>
          <BaseButton variant="outline" @click="setToday">Сегодня</BaseButton>
          <BaseButton variant="outline" @click="nextWeek" class="nav-btn">
            <span>След.</span>
            <AppIcon name="chevron-right" size="18" />
          </BaseButton>
        </div>
        
        <div class="filters">
          <div class="filter-item clickable" @click="showGroupSelect = true">
            <AppIcon name="user" size="16" class="filter-icon" />
            <span class="label">Группа:</span>
            <span class="value">{{ selectedGroupName }}</span>
          </div>
          <BaseButton 
            v-if="isEditMode" 
            variant="outline" 
            @click="showImportModal = true"
            class="import-btn"
          >
            <AppIcon name="activity" size="16" />
            Импорт
          </BaseButton>
        </div>
      </div>
    </header>

    <div class="schedule-grid">
      <div v-if="scheduleStore.isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Синхронизация...</p>
      </div>

      <div v-else class="days-container">
        <div v-for="day in groupedLessons" :key="day.date" class="day-column">
          <div class="day-header" :class="{ 'is-today': day.isToday }">
            <span class="day-name">{{ day.dayName }}</span>
            <span class="day-date">{{ day.displayDate }}</span>
            <button v-if="isEditMode" class="add-slot-btn" @click="openAddModal(day.date)">
              <AppIcon name="sparkles" size="14" />
            </button>
          </div>

          <div class="lessons-list">
            <div v-for="lesson in day.lessons" :key="lesson.id" class="lesson-card glass-panel" :class="{ 'editing': isEditMode }">
              <div class="lesson-time">
                <AppIcon name="clock" size="14" />
                <span class="start">{{ lesson.start_time.split('T')[1]?.slice(0, 5) }}</span>
                <span class="separator">-</span>
                <span class="end">{{ lesson.end_time.split('T')[1]?.slice(0, 5) }}</span>
              </div>
              <div class="lesson-details">
                <h4 class="subject">{{ lesson.title }}</h4>
                <div class="meta">
                  <span class="meta-item"><AppIcon name="location" size="12" /> {{ getAuditoriumName(lesson.auditorium_id) }}</span>
                  <span class="meta-item"><AppIcon name="user" size="12" /> {{ lesson.instructor }}</span>
                </div>
              </div>
              <div v-if="isEditMode" class="card-actions">
                <button class="action-icon del" @click="handleDelete(lesson.id)"><AppIcon name="logout" size="14" /></button>
                <button class="action-icon"><AppIcon name="settings" size="14" /></button>
              </div>
            </div>
            <div v-if="day.lessons.length === 0" class="no-lessons-day">Нет занятий</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка добавления -->
    <BaseModal :show="showAddModal" title="Добавить занятие" @close="showAddModal = false" @confirm="handleSaveSlot" :loading="isSaving">
      <div class="edit-form">
        <BaseInput label="Название предмета" v-model="slotForm.title" />
        <BaseInput label="Преподаватель" v-model="slotForm.instructor" />
        <div class="row">
          <BaseInput label="Время начала" type="time" v-model="slotForm.start_time" />
          <BaseInput label="Время конца" type="time" v-model="slotForm.end_time" />
        </div>
        <div class="select-group">
          <label class="styled-label">Аудитория</label>
          <select v-model="slotForm.auditorium_id" class="styled-select">
            <option v-for="aud in scheduleStore.auditoriums" :key="aud.id" :value="aud.id">{{ aud.name }}</option>
          </select>
        </div>
      </div>
    </BaseModal>

    <!-- Модалка выбора группы -->
    <BaseModal :show="showGroupSelect" title="Выберите группу" @close="showGroupSelect = false" confirmText="Выбрать" @confirm="showGroupSelect = false">
      <div class="group-select-grid">
        <div v-for="group in scheduleStore.groups" :key="group.id" class="group-option glass-panel" :class="{ 'active': selectedGroupId === group.id }" @click="selectedGroupId = group.id; showGroupSelect = false">
          <span class="group-name">{{ group.name }}</span>
          <span class="group-info">{{ group.instructor || 'Нет куратора' }}</span>
        </div>
      </div>
    </BaseModal>

    <!-- Модалка импорта -->
    <BaseModal :show="showImportModal" title="Импорт из Excel" @close="showImportModal = false" confirmText="Загрузить" @confirm="handleFileUpload" :loading="isUploading">
      <div class="import-form">
        <p class="description">Выберите .xlsx файл с расписанием. Система автоматически распознает группы и занятия.</p>
        <div class="file-upload-box glass-panel" :class="{ 'has-file': !!selectedFile }">
          <input type="file" id="schedule-file" @change="onFileChange" accept=".xlsx" hidden />
          <label for="schedule-file" class="file-label">
            <AppIcon name="dashboard" size="32" class="upload-icon" />
            <span class="file-name">{{ selectedFile ? selectedFile.name : 'Нажмите, чтобы выбрать файл' }}</span>
          </label>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { useAuthStore } from '../../../store/auth'
import { useScheduleStore } from '../../../store/schedule'
import BaseButton from '../../../core/components/BaseButton.vue'
import BaseInput from '../../../core/components/BaseInput.vue'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'
import api from '../../../core/utils/api'

const authStore = useAuthStore()
const scheduleStore = useScheduleStore()

const isAdmin = computed(() => authStore.user?.role?.toLowerCase() === 'admin')
const isEditMode = ref(false)
const currentBaseDate = ref(new Date())
const selectedGroupId = ref(1)
const showGroupSelect = ref(false)
const showAddModal = ref(false)
const showImportModal = ref(false)
const isSaving = ref(false)
const isUploading = ref(false)
const selectedFile = ref(null)

const slotForm = reactive({ date: '', title: '', instructor: '', start_time: '08:30', end_time: '10:00', auditorium_id: null })

const selectedGroupName = computed(() => {
  const g = scheduleStore.groups.find(g => g.id === selectedGroupId.value)
  return g ? g.name : 'Группа'
})

const getAuditoriumName = (id) => {
  const a = scheduleStore.auditoriums.find(aud => aud.id === id)
  return a ? a.name : (id || '—')
}

const groupedLessons = computed(() => {
  const days = []
  const startOfWeek = getMonday(currentBaseDate.value)
  const dayNames = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
  const todayStr = new Date().toISOString().split('T')[0]
  for (let i = 0; i < 6; i++) {
    const date = new Date(startOfWeek); date.setDate(startOfWeek.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    const lessonsForDay = scheduleStore.lessons.filter(l => l.start_time.startsWith(dateStr))
    days.push({
      date: dateStr,
      displayDate: date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }),
      dayName: dayNames[i],
      isToday: dateStr === todayStr,
      lessons: lessonsForDay.sort((a, b) => a.start_time.localeCompare(b.start_time))
    })
  }
  return days
})

function getMonday(d) {
  const date = new Date(d); const day = date.getDay();
  const diff = date.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(date.setDate(diff));
}

const fetchWeekData = async () => {
  const start = getMonday(currentBaseDate.value)
  const end = new Date(start); end.setDate(start.getDate() + 6)
  await scheduleStore.fetchSchedule({
    date_from: start.toISOString().split('T')[0],
    date_to: end.toISOString().split('T')[0],
    group_id: selectedGroupId.value
  })
}

const prevWeek = () => { currentBaseDate.value = new Date(currentBaseDate.value.setDate(currentBaseDate.value.getDate() - 7)) }
const nextWeek = () => { currentBaseDate.value = new Date(currentBaseDate.value.setDate(currentBaseDate.value.getDate() + 7)) }
const setToday = () => { currentBaseDate.value = new Date() }

const openAddModal = (date) => { slotForm.date = date; showAddModal.value = true }

const handleSaveSlot = async () => {
  isSaving.value = true
  try {
    const payload = {
      title: slotForm.title,
      instructor: slotForm.instructor,
      start_time: `${slotForm.date}T${slotForm.start_time}:00`,
      end_time: `${slotForm.date}T${slotForm.end_time}:00`,
      group_id: selectedGroupId.value,
      auditorium_id: slotForm.auditorium_id,
      status: 'scheduled'
    }
    await api.post('/schedule/', payload)
    await fetchWeekData()
    showAddModal.value = false
  } catch (e) { alert('Ошибка при сохранении') } finally { isSaving.value = false }
}

const handleDelete = async (id) => {
  if (!confirm('Удалить занятие?')) return
  await api.delete(`/schedule/${id}`)
  await fetchWeekData()
}

const onFileChange = (e) => { selectedFile.value = e.target.files[0] }
const handleFileUpload = async () => {
  if (!selectedFile.value) return
  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    await api.post('/schedule/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    await fetchWeekData()
    showImportModal.value = false; selectedFile.value = null; alert('Импорт завершен!')
  } catch (e) { alert('Ошибка импорта') } finally { isUploading.value = false }
}

watch(selectedGroupId, fetchWeekData)
watch(currentBaseDate, fetchWeekData)
onMounted(async () => {
  await scheduleStore.fetchGroups()
  await scheduleStore.fetchAuditoriums()
  await fetchWeekData()
})
</script>

<style scoped>
.schedule-container { max-width: 1400px; margin: 0 auto; }
.schedule-header { margin-bottom: 32px; }
.header-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
h1 { font-size: 2rem; font-weight: 800; margin: 0; }
.editor-toggle { display: flex; align-items: center; gap: 12px; background: rgba(255, 215, 0, 0.1); padding: 8px 16px; border-radius: 12px; border: 1px solid rgba(255, 215, 0, 0.2); }
.editor-toggle .label { font-size: 0.85rem; font-weight: 700; color: var(--primary-color); text-transform: uppercase; }
.switch { position: relative; display: inline-block; width: 40px; height: 20px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; inset: 0; background-color: rgba(255, 255, 255, 0.1); transition: .4s; border-radius: 20px; }
.slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: var(--primary-color); }
input:checked + .slider:before { transform: translateX(20px); background-color: #1C1B1F; }
.week-info { display: flex; align-items: center; gap: 16px; color: var(--text-secondary); }
.badge { background: var(--primary-color); color: #1C1B1F; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
.controls-section { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; margin-top: 20px; border-radius: 16px; }
.navigation { display: flex; gap: 8px; }
.filters { display: flex; gap: 16px; align-items: center; }
.filter-item { display: flex; align-items: center; gap: 10px; background: rgba(255, 255, 255, 0.05); padding: 8px 16px; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.filter-item:hover { background: rgba(255, 255, 255, 0.1); }
.days-container { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-top: 24px; }
.day-column { display: flex; flex-direction: column; gap: 16px; }
.day-header { padding: 12px; border-radius: 12px; background: rgba(255, 255, 255, 0.03); text-align: center; position: relative; display: flex; flex-direction: column; gap: 2px; }
.day-header.is-today { background: rgba(255, 215, 0, 0.15); border: 1px solid rgba(255, 215, 0, 0.3); }
.day-name { font-weight: 800; font-size: 0.9rem; }
.day-date { font-size: 0.75rem; opacity: 0.5; }
.add-slot-btn { position: absolute; right: -8px; top: -8px; width: 24px; height: 24px; border-radius: 50%; background: var(--primary-color); border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
.lesson-card { padding: 12px; border-radius: 16px; position: relative; border: 1px solid rgba(255, 255, 255, 0.05); }
.lesson-time { display: flex; align-items: center; gap: 4px; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.8rem; color: var(--primary-color); margin-bottom: 8px; }
.subject { margin: 0 0 8px 0; font-size: 0.9rem; font-weight: 700; line-height: 1.2; }
.meta { display: flex; flex-direction: column; gap: 4px; font-size: 0.75rem; color: var(--text-secondary); }
.meta-item { display: flex; align-items: center; gap: 4px; }
.card-actions { position: absolute; right: 8px; top: 8px; display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
.lesson-card:hover .card-actions { opacity: 1; }
.action-icon { background: rgba(0,0,0,0.3); border: none; width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; }
.action-icon.del:hover { background: rgba(255, 77, 79, 0.4); }
.no-lessons-day { text-align: center; padding: 20px; font-size: 0.75rem; color: var(--text-secondary); opacity: 0.3; border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 12px; }
.group-select-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; max-height: 400px; overflow-y: auto; padding: 4px; }
.group-option { padding: 16px; border-radius: 16px; cursor: pointer; text-align: center; transition: all 0.2s ease; border: 1px solid rgba(255, 255, 255, 0.05); }
.group-option:hover { background: rgba(255, 255, 255, 0.1); border-color: var(--primary-color); }
.group-option.active { background: var(--primary-color); color: #1C1B1F; }
.group-name { display: block; font-weight: 800; font-size: 1.1rem; }
.group-info { display: block; font-size: 0.75rem; opacity: 0.7; margin-top: 4px; }
.import-form { display: flex; flex-direction: column; gap: 16px; }
.file-upload-box { border: 2px dashed rgba(255, 215, 0, 0.3); border-radius: 20px; padding: 40px; text-align: center; transition: all 0.3s ease; }
.file-upload-box.has-file { border-color: var(--primary-color); background: rgba(255, 215, 0, 0.05); }
.file-label { display: flex; flex-direction: column; align-items: center; gap: 12px; cursor: pointer; }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(255, 215, 0, 0.1); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-state { text-align: center; padding: 100px 0; }
.edit-form { display: flex; flex-direction: column; gap: 16px; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.styled-select { width: 100%; padding: 12px; border-radius: 12px; background: var(--input-bg); color: white; border: 1px solid rgba(255,255,255,0.1); outline: none; }
@media (max-width: 1200px) { .days-container { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .days-container { grid-template-columns: 1fr; } }
</style>
