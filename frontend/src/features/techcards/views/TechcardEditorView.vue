<template>
  <div class="editor-page">
    <header class="editor-header animate-in">
      <div class="title-section">
        <BaseButton variant="outline" @click="$router.push('/techcards')" class="back-btn">
          <AppIcon name="chevron-left" size="18" />
        </BaseButton>
        <div>
          <h1>Конструктор техкарты</h1>
          <p class="id-badge mono">ID: #{{ $route.params.id }}</p>
        </div>
      </div>
      <div class="actions">
        <BaseButton variant="outline" @click="handleAutoFill" class="autofill-btn">
          <AppIcon name="sparkles" size="18" class="btn-icon" />
          Автозаполнение
        </BaseButton>
        <BaseButton @click="handleSave" :loading="isSaving">
          <AppIcon name="schedule" size="18" class="btn-icon" />
          Сохранить и Экспорт
        </BaseButton>
      </div>
    </header>

    <div class="editor-layout">
      <!-- Навигация по вкладкам -->
      <aside class="tabs-nav glass-panel">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: currentTab === tab.id }"
          @click="currentTab = tab.id"
        >
          <span class="tab-num">{{ tab.id }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </aside>

      <!-- Контент вкладок -->
      <main class="tab-content">
        <BaseCard class="glass-panel main-card">
          <!-- 1. Основная информация -->
          <div v-if="currentTab === 1" class="form-grid animate-fade">
            <div class="full-width">
              <BaseInput
                label="Тема занятия"
                v-model="form.tema"
                placeholder="Введите тему полностью..."
              />
            </div>
            <BaseInput label="Номер занятия" v-model="form.nomer_zanyatiya" />
            <div class="select-group">
              <label class="styled-label">Тип занятия</label>
              <select v-model="form.lesson_type_id" class="styled-select">
                <option :value="1">Теоретическое</option>
                <option :value="2">Практическое</option>
                <option :value="3">Лабораторное</option>
                <option :value="4">Контрольное</option>
              </select>
            </div>
            <div class="select-group">
              <label class="styled-label">Учебная группа</label>
              <select v-model="form.group_id" class="styled-select">
                <option v-for="g in scheduleStore.groups" :key="g.id" :value="g.id">
                  {{ g.name }}
                </option>
              </select>
            </div>
            <BaseInput
              label="Педагогические технологии"
              v-model="form.ped_tech"
              placeholder="Напр. проблемное обучение..."
            />
          </div>

          <!-- 2. Цели и задачи -->
          <div v-if="currentTab === 2" class="form-stack animate-fade">
            <BaseInput label="Цель занятия" v-model="form.cel_zanyatiya" />
            <div class="tasks-grid">
              <div class="task-item">
                <label class="styled-label">Обучающие задачи</label>
                <textarea
                  v-model="form.zadachi_obuch"
                  class="styled-textarea glass-panel"
                ></textarea>
              </div>
              <div class="task-item">
                <label class="styled-label">Развивающие задачи</label>
                <textarea
                  v-model="form.zadachi_razv"
                  class="styled-textarea glass-panel"
                ></textarea>
              </div>
              <div class="task-item">
                <label class="styled-label">Воспитательные задачи</label>
                <textarea
                  v-model="form.zadachi_vosp"
                  class="styled-textarea glass-panel"
                ></textarea>
              </div>
            </div>
            <BaseInput label="Прогноз результатов" v-model="form.prognoz_result" />
          </div>

          <!-- 3. Ресурсы -->
          <div v-if="currentTab === 3" class="form-stack animate-fade">
            <div class="task-item">
              <label class="styled-label">Оборудование и ПО</label>
              <textarea
                v-model="form.oborudovanie"
                class="styled-textarea glass-panel"
                placeholder="Проектор, ПК, Python 3.11..."
              ></textarea>
            </div>
            <div class="task-item">
              <label class="styled-label">Источники информации</label>
              <textarea
                v-model="form.istochniki"
                class="styled-textarea glass-panel"
                placeholder="Учебники, ссылки на документацию..."
              ></textarea>
            </div>
          </div>

          <!-- 4. Этапы занятия (ДИНАМИЧЕСКИЕ) -->
          <div v-if="currentTab === 4" class="stages-section animate-fade">
            <div class="stages-header">
              <h3>Ход занятия</h3>
              <BaseButton variant="outline" @click="addStage">
                <AppIcon name="sparkles" size="16" class="btn-icon" />
                Добавить этап
              </BaseButton>
            </div>

            <div class="stages-list">
              <div
                v-for="(stage, index) in form.stages"
                :key="index"
                class="stage-item glass-panel"
              >
                <div class="stage-top">
                  <span class="stage-index">Этап {{ index + 1 }}</span>
                  <input
                    v-model="stage.nazvanie_etapa"
                    class="stage-title-input"
                    placeholder="Название этапа..."
                  />
                  <input
                    v-model="stage.dlitelnost"
                    class="stage-time-input"
                    placeholder="Мин"
                    style="width: 60px"
                  />
                  <button @click="removeStage(index)" class="remove-btn">✕</button>
                </div>
                <div class="stage-grid">
                  <div class="sub-field">
                    <label>Деятельность преподавателя</label>
                    <textarea v-model="stage.deyatelnost_prepod"></textarea>
                  </div>
                  <div class="sub-field">
                    <label>Деятельность студентов</label>
                    <textarea v-model="stage.deyatelnost_obuch"></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </BaseCard>
      </main>
    </div>

    <!-- Модалка автозаполнения -->
    <BaseModal
      :show="showAutofill"
      title="Выбор занятия"
      @close="showAutofill = false"
      @confirm="applyAutofill"
    >
      <p class="hint">
        Выберите занятие из расписания, чтобы подтянуть тему, группу и преподавателя.
      </p>
      <div class="autofill-list">
        <div
          v-for="lesson in scheduleStore.lessons"
          :key="lesson.id"
          class="autofill-item glass-panel"
          @click="selectedLesson = lesson"
          :class="{ active: selectedLesson?.id === lesson.id }"
        >
          <span class="date">{{ lesson.start_time.split('T')[0] }}</span>
          <span class="title">{{ lesson.title }}</span>
          <span class="grp">{{ lesson.instructor }}</span>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTechcardStore } from '../../../store/techcard'
import { useScheduleStore } from '../../../store/schedule'
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseButton from '../../../core/components/BaseButton.vue'
import BaseInput from '../../../core/components/BaseInput.vue'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const route = useRoute()
const router = useRouter()
const techcardStore = useTechcardStore()
const scheduleStore = useScheduleStore()

const currentTab = ref(1)
const isSaving = ref(false)
const showAutofill = ref(false)
const selectedLesson = ref(null)

const tabs = [
  { id: 1, label: 'Общая информация' },
  { id: 2, label: 'Цели и задачи' },
  { id: 3, label: 'Ресурсы и материалы' },
  { id: 4, label: 'Этапы занятия' }
]

const form = reactive({
  tema: '',
  nomer_zanyatiya: '1',
  lesson_type_id: 1,
  group_id: 1,
  ped_tech: '',
  cel_zanyatiya: '',
  zadachi_obuch: '',
  zadachi_razv: '',
  zadachi_vosp: '',
  prognoz_result: '',
  oborudovanie: '',
  istochniki: '',
  stages: [
    {
      nazvanie_etapa: 'Организационный момент',
      dlitelnost: '5',
      deyatelnost_prepod: 'Приветствие, проверка присутствующих',
      deyatelnost_obuch: 'Подготовка к занятию',
      cel_etapa: '',
      formiruemye_kompetencii: '',
      nomer_etapa: 1
    }
  ]
})

const addStage = () => {
  form.stages.push({
    nazvanie_etapa: '',
    dlitelnost: '10',
    deyatelnost_prepod: '',
    deyatelnost_obuch: '',
    cel_etapa: '',
    formiruemye_kompetencii: '',
    nomer_etapa: form.stages.length + 1
  })
}

const removeStage = index => {
  form.stages.splice(index, 1)
}

const handleAutoFill = () => {
  scheduleStore.fetchUpcoming()
  showAutofill.value = true
}

const applyAutofill = () => {
  if (!selectedLesson.value) return
  form.tema = selectedLesson.value.title
  form.group_id = selectedLesson.value.group_id
  showAutofill.value = false
}

const handleSave = async () => {
  isSaving.value = true
  try {
    if (route.params.id === 'new') {
      const created = await techcardStore.createCard({ ...form })
      router.replace(`/techcards/${created.id}`)
    } else {
      await techcardStore.saveCard(route.params.id, { ...form })
    }
    alert('Карта сохранена!')
  } catch (e) {
    alert('Ошибка сохранения')
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  await scheduleStore.fetchGroups()
  // Новая карта — создаётся при сохранении
  if (route.params.id === 'new') return
  // Если редактируем существующую
  try {
    const data = await techcardStore.fetchCardById(route.params.id)
    if (data) Object.assign(form, data)
  } catch (e) {
    /* Игнорируем если новая */
  }
})
</script>

<style scoped>
.editor-page {
  max-width: 1400px;
  margin: 0 auto;
}
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}
.title-section {
  display: flex;
  align-items: center;
  gap: 20px;
}
h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
}
.id-badge {
  font-size: 0.8rem;
  opacity: 0.5;
  margin-top: 4px;
}

.actions {
  display: flex;
  gap: 12px;
}
.back-btn {
  padding: 8px;
  min-height: auto;
}

.editor-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 32px;
  align-items: start;
}

.tabs-nav {
  padding: 12px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 14px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}
.tab-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}
.tab-btn.active {
  background: var(--primary-color);
  color: #1c1b1f;
  font-weight: 700;
}
.tab-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.main-card {
  padding: 40px;
  min-height: 600px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.full-width {
  grid-column: span 2;
}
.form-stack {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.tasks-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}
.styled-textarea {
  width: 100%;
  min-height: 120px;
  padding: 16px;
  border-radius: 16px;
  background: var(--input-bg);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  outline: none;
}

.stages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.stage-item {
  padding: 24px;
  border-radius: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.stage-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.stage-index {
  font-weight: 800;
  color: var(--primary-color);
  font-size: 0.85rem;
  text-transform: uppercase;
}
.stage-title-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  outline: none;
}
.stage-time-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 4px 8px;
  color: white;
  text-align: center;
}

.stage-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.sub-field label {
  display: block;
  font-size: 0.8rem;
  opacity: 0.6;
  margin-bottom: 8px;
  font-weight: 600;
}
.sub-field textarea {
  width: 100%;
  min-height: 80px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  color: white;
  padding: 12px;
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
}

.remove-btn {
  background: transparent;
  border: none;
  color: #ff4d4f;
  cursor: pointer;
  font-size: 1.2rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.remove-btn:hover {
  opacity: 1;
}

.autofill-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
}
.autofill-item {
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid transparent;
}
.autofill-item:hover {
  background: rgba(255, 255, 255, 0.05);
}
.autofill-item.active {
  border-color: var(--primary-color);
  background: rgba(255, 215, 0, 0.05);
}
.autofill-item .title {
  font-weight: 700;
}
.autofill-item .date {
  font-size: 0.8rem;
  opacity: 0.5;
}

.animate-fade {
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1000px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }
  .tabs-nav {
    flex-direction: row;
    overflow-x: auto;
  }
  .tasks-grid {
    grid-template-columns: 1fr;
  }
}
</style>
