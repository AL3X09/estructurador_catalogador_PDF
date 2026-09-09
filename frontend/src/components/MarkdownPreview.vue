<template>
  <div class="preview-container">
    <h2>Vista Previa del Documento</h2>

    <div v-if="loading" class="status">Cargando contenido...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>
    <div v-else-if="!markdownContent" class="status">
      Selecciona un documento de la lista para ver su contenido.
    </div>

    <div v-else class="markdown-body" v-html="renderedMarkdown"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { marked } from 'marked';
import axios from 'axios';

const props = defineProps({
  documentId: {
    type: String,
    default: null
  }
});

const markdownContent = ref('');
const loading = ref(false);
const error = ref('');

// Computed property para compilar el markdown a HTML
const renderedMarkdown = computed(() => {
  return markdownContent.value ? marked.parse(markdownContent.value) : '';
});

// Observar cambios en el documentId para cargar su contenido
watch(() => props.documentId, async (newId) => {
  if (!newId) {
    markdownContent.value = '';
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    // Al no estar servido por FastAPI estáticamente en la API (los endpoints solo devuelven el JSON catalogado),
    // Simularemos la lectura sirviendo estáticamente de ser necesario, pero para evitar problemas de rutas en Vue+Vite dev,
    // lo más seguro es usar un import dinámico si se pudiera, o un fetch si FastAPI sirve estáticos.
    // Como FastAPI no está configurado para servir 'knowledge_base' por defecto, añadiremos un endpoint ad-hoc
    // O mejor, obtendremos el archivo por medio del servidor estático si estuviera expuesto.
    // Vamos a solicitarle a Axios que haga un GET al markdown estático (requiere que FastAPI lo sirva).
    // Asumiremos que el backend expone el archivo en /knowledge_base/{id}/document.md
    const response = await axios.get(`http://localhost:8000/knowledge_base/${newId}/document.md`);
    markdownContent.value = response.data;
  } catch (err) {
    console.error("Error cargando markdown:", err);
    error.value = 'No se pudo cargar el contenido del documento.';
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.preview-container {
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #fff;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.status {
  padding: 20px;
  text-align: center;
  color: #666;
  margin-top: 50px;
}

.error {
  color: #721c24;
  background-color: #f8d7da;
  border-radius: 4px;
}

.markdown-body {
  flex-grow: 1;
  overflow-y: auto;
  padding-right: 15px;
  line-height: 1.6;
  color: #333;
}

/* Estilos básicos para el markdown renderizado */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 15px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 6px 13px;
}

.markdown-body :deep(th) {
  background-color: #f6f8fa;
}

.markdown-body :deep(pre) {
  background-color: #f6f8fa;
  padding: 16px;
  overflow: auto;
  border-radius: 3px;
}
</style>
