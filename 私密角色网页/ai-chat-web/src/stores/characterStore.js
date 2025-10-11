import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getStorage, setStorage, KEYS } from '../utils/storage'
import { DEFAULT_AVATARS } from '../utils/api'

export const useCharacterStore = defineStore('character', () => {
  // 状态
  const characters = ref({}) // { cartoon_id: characterData }

  // 初始化：从localStorage加载数据
  function initialize() {
    const savedCharacters = getStorage(KEYS.CHARACTERS)
    if (savedCharacters) {
      characters.value = savedCharacters
    }
  }

  // 创建新角色
  function createCharacter(cartoonId, characterImage = null) {
    const newCharacter = {
      cartoon_id: cartoonId,
      character_image: characterImage || DEFAULT_AVATARS[0],
      character_profile: {
        name: null,
        gender: null,
        identity: null,
        personality_traits: null,
        speaking_style: null,
        background_story: null,
        relationship_with_user: null,
        additional_info: null
      },
      draft: false,
      created_at: Date.now(),
      updated_at: Date.now()
    }

    characters.value[cartoonId] = newCharacter
    saveToStorage()
    return newCharacter
  }

  // 获取角色
  function getCharacter(cartoonId) {
    return characters.value[cartoonId] || null
  }

  // 更新角色
  function updateCharacter(cartoonId, updates) {
    if (characters.value[cartoonId]) {
      Object.assign(characters.value[cartoonId], updates)
      characters.value[cartoonId].updated_at = Date.now()
      saveToStorage()
      return true
    }
    return false
  }

  // 删除角色
  function deleteCharacter(cartoonId) {
    if (characters.value[cartoonId]) {
      delete characters.value[cartoonId]
      saveToStorage()
      return true
    }
    return false
  }

  // 保存到localStorage
  function saveToStorage() {
    setStorage(KEYS.CHARACTERS, characters.value)
  }

  return {
    // 状态
    characters,

    // 方法
    initialize,
    createCharacter,
    getCharacter,
    updateCharacter,
    deleteCharacter,
    saveToStorage
  }
})
