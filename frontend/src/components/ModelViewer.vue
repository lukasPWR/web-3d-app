<script setup>
import { ref, defineProps, onMounted } from 'vue'
import { useGLTF } from '@tresjs/cientos'

const props = defineProps({
  modelPath: {
    type: String,
    required: true
  }
})

const { scene, nodes, materials } = useGLTF(props.modelPath)
const model = ref(null)

onMounted(() => {
  if (scene.value) {
    model.value = scene.value
  }
})
</script>

<template>
  <TresMesh v-if="model" :geometry="model.geometry" :material="model.material" :position="[0, 0, 0]" :scale="[1, 1, 1]" :rotation="[-Math.PI / 2, 0, 0]" />
  <TresGroup v-else>
    <TresBox :position="[0, 0, 0]">
      <TresMeshStandardMaterial color="#1e88e5" />
    </TresBox>
    <TresSphere :position="[2, 0, 0]" :radius="0.8">
      <TresMeshStandardMaterial color="#43a047" />
    </TresSphere>
    <TresCone :position="[-2, 0, 0]" :radius="0.8" :height="1.5">
      <TresMeshStandardMaterial color="#e53935" />
    </TresCone>
  </TresGroup>
</template>
