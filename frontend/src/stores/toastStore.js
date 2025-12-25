import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const show = ref(false)
  const message = ref('')
  const type = ref('success') // 'success' or 'error'

  const showToast = (msg, toastType = 'success') => {
    message.value = msg
    type.value = toastType
    show.value = true

    // 3초 후 자동으로 숨김
    setTimeout(() => {
      show.value = false
    }, 3000)
  }

  return {
    show,
    message,
    type,
    showToast,
  }
})
